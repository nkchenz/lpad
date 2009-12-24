#!/usr/bin/python
#encoding: utf8
"""
LPad: My music player for linux.
CopyRight (C) 2008 Chen Zheng <nkchenz@gmail.com>
 
Distributed under terms of GPL v2
"""

import pygtk
import os
pygtk.require('2.0')
import gtk
import gobject
import pango
import glob
from lyric import *
from mslave import *
import time
import urllib
import random
import thread
import fcntl
import commands
import json

from misc import *
from cue import *
import engine
import compress
import version

LP_NAME = 'LPad' 
LP_VERSION = version.version
LP_CODE_NAME = version.codename
LP_WIDTH = 225
LP_HEIGHT = 400

LP_PLAYLIST_TEXT = '#17E8F1'
LP_PLAYLIST_BACKGROUND = '#000000'
LP_PLAYLIST_EXT = '.sl'
LP_PLAYLIST_DEFAULT_FILE = '~/.ListenPad/default' + LP_PLAYLIST_EXT
LYRIC_REPO_PATH = '~/.ListenPad/repo'
LP_SUPPORT_EXTS = ['.mp3', '.ape', '.flac', '.ogg', '.wma', '.rar', LP_PLAYLIST_EXT]

# For drag and drop files to playlist
TARGET_TYPE_URI_LIST = 80
dnd_list = [('text/uri-list', 0, TARGET_TYPE_URI_LIST)]

def get_file_path_from_dnd_dropped_uri(uri):
    path = urllib.url2pathname(uri) # escape special chars
    path = path.strip('\r\n\x00') # remove \r\n and NULL

    # get the path to file
    if path.startswith('file:\\\\\\'): # windows
            path = path[8:] # 8 is len('file:///')
    elif path.startswith('file://'): # nautilus, rox
            path = path[7:] # 7 is len('file://')
    elif path.startswith('file:'): # xffm
            path = path[5:] # 5 is len('file:')
    return path

def log(s):
    debug_view.log(to_utf8(s))

def insert_one_tag_into_buffer(buffer, name, *params):
    tag = gtk.TextTag(name)
    while(params):
        tag.set_property(params[0], params[1])
        params = params[2:]
    table = buffer.get_tag_table()
    table.add(tag)

def create_tags (buffer):
    insert_one_tag_into_buffer(buffer, "playing",
                            "weight", pango.WEIGHT_BOLD,
                            "foreground", "white")
    insert_one_tag_into_buffer(buffer, "none")

class Menu:
    ui = '''<ui>
    <menubar name="MenuBar">
      <menu action="File">
        <menuitem action="SaveList"/>
        <menuitem action="LoadList"/>
        <menuitem action="AddDir"/>
        <menuitem action="AddFile"/>
        <menuitem action="ClearList"/>
        <menuitem action="Quit"/>
      </menu>
      <menu action="View">
        <menuitem action="Debug"/>
        <menuitem action="Lyric"/>
        <separator/>
      </menu>
     <menu action="Help">
        <menuitem action="About"/>
      </menu>
     </menubar>
    </ui>'''
      
    def __init__(self, proxy):
        self.proxy = proxy # We use this proxy to get controller, which contains all the refs needed
        # Creat ui, accelerate keys group
        self.uimanager = gtk.UIManager()
        self.accelgroup = self.uimanager.get_accel_group()

        # Bind 'action' in ui define string or file
        self.actiongroup = gtk.ActionGroup(LP_NAME)
        self.actiongroup.add_actions(
            [('File', None, '_File'),
            ('SaveList', None, '_Save List', None, '', self.OnSaveList),
            ('LoadList', None, '_Load List', None, '', self.OnLoadList),
            ('AddDir', None, 'Add _Dir', None, '', self.OnAddDir),
            ('AddFile', None, 'Add _File', None, '', self.OnAddFile),
            ('ClearList', None, '_Clear List', None, '', self.OnClear),
            ('Quit', gtk.STOCK_QUIT, '_Quit', None, '', self.OnQuit),
            ('View', None, '_View'),
            ('Help', None, '_Help'),
            ('About', None, '_About', None, '', self.OnAbout),])

        # Create a ToggleAction, etc.
        self.actiongroup.add_toggle_actions([('Debug', None, '_Debug', '', 'Show Debug Window', self.OnDebug),
                                        ('Lyric', None, '_Lyric', '', 'Show Lyric Window', self.OnLyric),])

        self.uimanager.insert_action_group(self.actiongroup, 0)
        
        # Load ui
        self.uimanager.add_ui_from_string(self.ui)
        self.menubar = self.uimanager.get_widget('/MenuBar')

    def OnSaveList(self, event):
        dialog = gtk.FileChooserDialog(title='Save play list', \
                    action=gtk.FILE_CHOOSER_ACTION_SAVE,
                    buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,\
                              gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            file = dialog.get_filename()
            if not file.endswith(LP_PLAYLIST_EXT):
                file += LP_PLAYLIST_EXT
            self.proxy.playlist_view.save(file)
            log('Playlist %s saved' % file)
        dialog.destroy()

    def OnLoadList(self, event):
        dialog = gtk.FileChooserDialog(title='Load play list', \
                    action=gtk.FILE_CHOOSER_ACTION_OPEN,
                    buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,\
                              gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    
        filter = gtk.FileFilter()
        filter.add_pattern("*%s" % LP_PLAYLIST_EXT)
        dialog.set_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            file = dialog.get_filename()
            if not file.endswith(LP_PLAYLIST_EXT):
                log('Unknown playlist format %s' % file)
                return 
            self.proxy.playlist_view.load(file)
            log('Playlist %s loaded' % file)
        dialog.destroy()

    def OnDebug(self, event):
        if event.get_active():
            self.proxy.debug_view.window.show_all()
        else:
            self.proxy.debug_view.window.hide()

    def change_state(self, var, value):
        self.actiongroup.get_action(var).set_active(value)

    def OnLyric(self, event):
        if event.get_active():
            self.proxy.lyric_view.window.show()
        else:
            self.proxy.lyric_view.window.hide()

    def OnQuit(self, event):
        # Fixme: we should call the quit function of main window do some clean work
        self.proxy.delete_event(None, None)

    def OnAddDir(self, event):
        dialog = gtk.FileChooserDialog(title='Which dir do you want to add?', \
                    action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,\
                    buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,\
                              gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            dir = dialog.get_filename()
            self.proxy.playlist_view.add(dir)
        dialog.destroy()

    def OnAddFile(self, event):
        dialog = gtk.FileChooserDialog(title='Which files do you want to add?', \
                    action=gtk.FILE_CHOOSER_ACTION_OPEN,\
                    buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,\
                              gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_select_multiple(True)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            files = dialog.get_filenames()
            for f in files:
                self.proxy.playlist_view.add(f)
        dialog.destroy()

    def OnClear(self, event):
        self.proxy.playlist_view.songlist = []
        self.proxy.playlist_view.sync_songlist()

    def OnAbout(self, event):
        about = gtk.AboutDialog()
        infos = {
            'name': LP_NAME,
            'version': LP_VERSION,
            'copyright': '(C) 2008 Chen Zheng',
            'license': 'GPL v2',
            'website': 'http://code.google.com/p/lpad',
            'authors': ['Chen Zheng <nkchenz@gmail.com>'],
            'comments': 'My music player for linux\nCodeName: %s' % LP_CODE_NAME,
            }
        for k, v in infos.items():
            name = 'set_' + k
            setter = getattr(about, name)
            setter(v)
        about.run()
        about.hide()


class LyricChooser:
    def __init__(self, parent):
        self.parent = parent # Lyric Show window
        self.ti = self.parent.curr_ti

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('Choose lyrics')
        #self.window.connect("delete_event", self.hide_on_close)
        self.window.set_size_request(int(LP_WIDTH * 1.5), int(LP_HEIGHT * 0.8))
        self.window.set_position(gtk.WIN_POS_CENTER)

        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
     

        self.liststore = gtk.ListStore(str, str, str)
        self.treeview = gtk.TreeView(self.liststore)

        style = gtk.CellRendererText()
        col = gtk.TreeViewColumn('artist', style, text = 1)
        self.treeview.append_column(col)
        col = gtk.TreeViewColumn('title', style, text = 2)
        self.treeview.append_column(col)
        col = gtk.TreeViewColumn('link', style, text = 0)
        self.treeview.append_column(col)

        #self.treeview.set_reorderable(True)
        self.treeview.columns_autosize()
        self.treeview.set_enable_search(False)
        self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
        self.treeview.connect('row-activated', self.selection)
        self.sw.add(self.treeview)

        for song in self.parent.download_links:
            self.liststore.append([song[0], song[2], song[1]])

        vbox = gtk.VBox()
        vbox.pack_start(self.sw, True, True, 1)
        
        hbox = gtk.HBox()

        button = gtk.Button('Close')
        button.connect('clicked', self.OnClose)
        hbox.pack_end(button, False, False, 1)

        button = gtk.Button('OK')
        button.connect('clicked', self.OnOK)
        hbox.pack_end(button, False, False, 1)

        vbox.pack_start(hbox, False, False, 1)
        self.window.add(vbox)

    def OnClose(self, w):
        self.window.destroy()

    def replace_lyric(self, link):
        if self.ti != self.parent.curr_ti: # the song has changed, so do nothing
            return
        self.parent.clear()
        self.parent.update_lyric(link)

    def OnOK(self, w):
        liststore, items =  self.treeview.get_selection().get_selected_rows()
        link = liststore[items[0][0]][0]
        # Use thread here to shutdown this window immediately
        # Let the background thread handle lyric replacing
        #     
        #    thread.start_new_thread(self.replace_lyric, (link))
        # TypeError: 2nd arg must be a tuple
        # So we use (link, ) here, don't panic
        thread.start_new_thread(self.replace_lyric, (link,))
        self.window.destroy()
        
    def selection(self, path, col, item):
        id = col[0]
        link = self.liststore[id][0]
        thread.start_new_thread(self.replace_lyric, (link,))
        self.window.destroy()
 

class DebugWindow:
    """
    Debug info window
    """
    def __init__(self):
        self.proxy = None
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('Debug-' + LP_NAME)
        self.window.set_size_request(LP_WIDTH * 2, LP_HEIGHT / 2)
        self.window.connect("delete_event", self.hide_on_close)

        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textview = gtk.TextView()

        self.textview.set_editable(False)
        #self.textview.set_cursor_visible(False)
        #self.textview.set_justification(gtk.JUSTIFY_CENTER)

        self.textbuffer = self.textview.get_buffer()
        self.textview.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))
        self.textview.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))

        self.sw.add(self.textview)
        self.sw.show()
        self.textview.show()
        
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(self.sw, True, True, 1)
        vbox.show()
        self.window.add(vbox)
        # Don't show us at the task list 
        #self.window.set_skip_taskbar_hint(True)
    
    def hide_on_close(self, a, b):
        self.window.hide()
        if self.proxy:
            self.proxy.menu.change_state('Debug', False)
        return True

    def log(self, s):
        pos = self.textbuffer.get_end_iter()
        #self.textbuffer.insert(pos, '%s %s\n' % (time.ctime(), s))
        self.textbuffer.insert(pos, '%s\n' % (s))
        self.textview.scroll_to_iter(self.textbuffer.get_end_iter(), 0, True, 1.0, 0.8)
 

class LyricView:

    def __init__(self, proxy):
        self.proxy = proxy

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('Lyric-' + LP_NAME)
        self.window.set_size_request(LP_WIDTH * 2, LP_HEIGHT)
        self.window.connect("delete_event", self.hide_on_close)

        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textview = gtk.TextView()

        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.set_justification(gtk.JUSTIFY_CENTER)

        self.textbuffer = self.textview.get_buffer()
        self.textview.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('#000000'))
        self.textview.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('blue'))
        create_tags(self.textbuffer)

        self.sw.add(self.textview)
        self.sw.show()
        self.textview.show()
        
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(self.sw, True, True, 1)
        
        hbox = gtk.HBox(False, 0)

        self.engines_btn = []
        tmp = gtk.Label('歌词引擎')
        hbox.pack_start(tmp, False, False, 1)
        eng = gtk.RadioButton(None, "Baidu")
        self.engines_btn.append(eng)
        eng.set_active(True)
        hbox.pack_start(eng, False, False, 1)
        eng = gtk.RadioButton(eng, "Google")
        self.engines_btn.append(eng)
        hbox.pack_start(eng, False, False, 1)
        eng.connect('clicked', self.choose_search_engine)
    
        button = gtk.Button('More')
        button.connect('clicked', self.hide_tool_panel)
        hbox.pack_end(button, False, False, 1)
        # Show all the widgets in a container: show_all
        # Show widgets only call 'show' explictly in a container: show
        hbox.show_all()
        vbox.pack_start(hbox, False, False, 1)
        
        #separator = gtk.HSeparator()
        
        tool = gtk.VBox(False, 0)

        #hbox = gtk.HBox(False, 0)
        #hbox.set_alignment('center')

        hbox = gtk.HBox(False, 0)
        entry = gtk.Entry()
        entry.set_max_length(100)
        entry.set_size_request(LP_WIDTH * 3 / 4, -1)
        entry.connect('activate', self.search_again)
        hbox.pack_start(entry, False, False, 1)
        self.keywords_view = entry

        button = gtk.Button('重新搜索')
        button.connect('clicked', self.search_again)
        hbox.pack_start(button, False, False, 1)

        button = gtk.Button('关联本地歌词')
        button.connect('clicked', self.choose_lyric_local)
        hbox.pack_end(button, False, False, 1)

        button = gtk.Button('选择搜索结果')
        button.connect('clicked', self.choose_lyric_manually)
        hbox.pack_end(button, False, False, 1)

        tool.pack_start(hbox, False, False, 1)


        hbox = gtk.HBox(False, 0)
        entry = gtk.Entry()
        entry.set_text('我想听')
        entry.set_max_length(100)
        hbox.pack_start(entry, False, False, 1)
        self.iwant = entry
        #tool.pack_start(hbox, False, False, 1)
        
        tool.set_size_request(LP_WIDTH * 2, int(LP_HEIGHT * 0.25))
        vbox.pack_start(tool, False, False, 1)
        self.tool_panel = tool
        vbox.show()

        self.window.add(vbox)
        self.tool_panel.hide()
        #self.window.set_skip_taskbar_hint(True) # If you don't want lyric window show on taskbar, uncomment this line

        self.repo = LyricRepo(LYRIC_REPO_PATH)
        self.last_line = None
        self.curr_ar = None
        self.curr_ti = None
        self.download_links = None

        # For lyric search engine
        self.current_engine = 'baidu'
        self.engines = {'baidu': engine.BaiduEngine(),
                'google': engine.GoogleEngine()}

    def foo(self, a):
        # So ugly here, how do you use start_new_thread to start a function need no args?
        # start_new_thread requires 2nd arg must be a tuple, but, show_lyric only expect 1 args!
        self.show_lyric()

    def choose_search_engine(self, widget):
        for btn in self.engines_btn:
            if btn.get_active():
                log('Choosen %s' % btn.get_label())
                self.current_engine = btn.get_label().lower()
                break

    def choose_lyric_local(self, widget):
        dialog = gtk.FileChooserDialog(title='Please choose the .lrc file', \
                    action=gtk.FILE_CHOOSER_ACTION_OPEN,
                    buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,\
                              gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    
        filter = gtk.FileFilter()
        filter.add_pattern("*.lrc")
        dialog.set_filter(filter)

        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            file = dialog.get_filename()
            # Save it
            f = open(file, 'r')
            self.repo.save_lyric(self.curr_ar, self.curr_ti, f.read())
            f.close()
            log('Local lyric file selected %s' % file)
            thread.start_new_thread(self.foo, (1,))
        dialog.destroy()

    def choose_lyric_manually(self, widget):
        if self.download_links is None:
            log('Nothing to chooose, it\'s only used to choose between auto search results')
            return
        w = LyricChooser(self)
        w.window.show_all()
        pass

    def hide_tool_panel(self, widget):
        action = widget.get_label()
        if action == 'Hide':
            self.tool_panel.hide()
            widget.set_label('More')
        else:
            self.tool_panel.show_all()
            widget.set_label('Hide')

    def search_again(self, widget):
        self.clear()
        keywords = self.keywords_view.get_text()
        log('search again, keywords: ' + keywords)
        if self.curr_ar != None and keywords:
            thread.start_new_thread(self.search_internet, ('', keywords))

    def hide_on_close(self, a, b):
        # Dont care what 'a' 'b' really are
        self.window.hide()
        self.proxy.menu.change_state('Lyric', False)
        return True 

    def scroll_lyric(self, pos):
        '''Called every one second when updating progress bar'''
        # No lyric found
        if not self.lyric:
            return
        l = self.lyric['lyrics']
        for i in range(0, len(l)):
            timestamp, text = l[i]
            min, sec = timestamp.split(':')
            sec = int(min) * 60 + float(sec)
            if sec >= pos:
                if sec > pos + 1:
                    return # Too early
                tmp = text.strip()
                if tmp is '': # Blank
                    continue
                self.show_line(i)
                return

    def show_line(self, line):
        # Reset the style of last line
        if self.last_line != None:
            self.change_line_style(self.last_line, 'playing', remove = True)
        self.last_line = line

        self.change_line_style(line, 'playing')

        # Scroll to middle
        iter = self.textbuffer.get_iter_at_line(line)
        mark = self.textbuffer.create_mark(None, iter)
        self.textview.scroll_to_mark(mark, 0, use_align=True, xalign=0.5, yalign=0.5)

    def change_line_style(self, line, tag, remove = False):
        start = self.textbuffer.get_iter_at_line(line)
        end = self.textbuffer.get_iter_at_line(line + 1)
        if end == None:
            end = self.textbuffer.get_end_iter()
        if remove:
            self.textbuffer.remove_tag_by_name(tag, start, end)
        else:
            self.textbuffer.apply_tag_by_name(tag, start, end)

    def search_internet(self, ar, ti):
        #print 'thread se started'
        self.add_line('Searching from %s' % self.current_engine)
        self.add_line('%s %s' % (ar, ti))

        links = self.engines[self.current_engine].search_lrc(ar, ti)
        if not links:
            self.add_line('Nothing found')
            return

        self.download_links = links
        for link in links:
             self.add_line('href=%s artist=%s title=%s' % (link[0], link[2], link[1]))
        
        href = links[0][0]
        self.update_lyric(href)

    def update_lyric(self, href):
        self.add_line('Select ' + href)
        data = self.repo.download_lrc(href)
        if data == None:
            self.add_line('Download error')
            return

        # ar, ti should be the same as self.ar, self.ti
        # For keywords search's consideration of user, we need to save lrc to its original 
        # ar, ti path, because we did not modify its mp3 tag, so next time it still will be
        # the wrong tags.

        ar, ti = self.curr_ar, self.curr_ti
        self.add_line('Saving to ' + self.repo.get_path(ar, ti))
        self.repo.save_lyric(ar, ti, data)
        self.add_line('Done, reloading')
        time.sleep(1)
        
        # Lyric has been saved, so call show_lyric again it will find it in local repo
        # it shall not cause infinite loop
        self.show_lyric()

    def add_line(self, line):
        pos = self.textbuffer.get_end_iter()
        self.textbuffer.insert(pos, line + '\n')
        log(line)
    
    def clear(self):
        # Clear lyric window first
        start, end = self.textbuffer.get_bounds()
        self.textbuffer.delete(start, end)

    def show_lyric(self):
        artist, title = self.curr_ar, self.curr_ti
        self.clear()
        l = self.repo.get_lyric(artist, title)
        self.lyric = l
        if l == None:
            log('Lyric not found')
            self.add_line('%s\n没有找到歌词' % self.repo.get_path(artist, title))
            #gobject.idle_add(self.search_internet)
            #se = threading.Thread(target = self.search_internet, args=(artist, title))
            #se.start()
            thread.start_new_thread(self.search_internet, (artist, title))

            #gobject.timeout_add(10, self.search_internet, artist, title) # Start a new one
            return

        pos = self.textbuffer.get_start_iter()
        log('Show Lyric ' + artist +  title)
        for timestamp, text in l['lyrics']:
            self.textbuffer.insert(pos, timestamp + text + '\n')

class PlayListView:
    def __init__(self, proxy):

        self.default_playlist = os.path.expanduser(LP_PLAYLIST_DEFAULT_FILE)

        self.proxy = proxy # Controller
        self.cds = {} # Cue files cache

        self.liststore = gtk.ListStore(str) # title only
        self.songlist = []
        self.treeview = gtk.TreeView(self.liststore)

        style = gtk.CellRendererText()
        style.set_property('cell-background', 'black')
        style.set_property('foreground', LP_PLAYLIST_TEXT)

        # text is index of the item in liststore
        self.column_name = gtk.TreeViewColumn('NAME', style, text = 0)
        self.treeview.append_column(self.column_name)
        self.treeview.set_enable_search(False)
        #self.treeview.set_search_column(0)
        self.column_name.set_sort_column_id(0)
        self.treeview.set_headers_visible(False)

        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.treeview.connect('row-activated', self.selection)
        self.treeview.connect('key_press_event', self.short_cuts)

        self.treeview.connect('drag_data_received', self.on_drag_data_received)
        self.treeview.drag_dest_set(gtk.DEST_DEFAULT_MOTION | gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
                                     dnd_list, gtk.gdk.ACTION_COPY)

    def on_drag_data_received(self, widget, context, x, y, selection, target_type, timestamp):
        if target_type == TARGET_TYPE_URI_LIST:
                uri = selection.data.strip()
                log('uri: %s' % uri)
                uri_splitted = uri.split() # we may have more than one file dropped
                for uri in uri_splitted:
                        self.add(get_file_path_from_dnd_dropped_uri(uri))

    def short_cuts(self, data, event):
        if event.type == gtk.gdk.KEY_PRESS:
            key = event.keyval

            if key == ord('s') or key == ord('S'):
                self.save(self.default_playlist)

            # Multiple delete with  'd', 'D', 'Delete'
            if key == ord('d') or key == ord('D') or key == 65535:
                _, items =  self.treeview.get_selection().get_selected_rows()
                # Delete indexes list in items
                deleted = [x[0] for x in items]
                self.songlist = [ x for x in self.songlist if self.songlist.index(x) not in deleted]
                self.sync_songlist()

    def check_file(self, file):
        # If file exists and type is supportted, return True. Else return False
        self.support_types = LP_SUPPORT_EXTS
        return os.path.isfile(file) and os.path.splitext(file)[1].lower() in self.support_types

    def sync_songlist(self):
        log('Syncing songlist')
        self.liststore.clear()
        for x in self.songlist:
            self.liststore.append([x['title']])

    def selection(self, path, col, item):
        id = col[0]
        file = self.songlist[id]['path']
        # Stop first
        #self.proxy.player.play_stop()
        self.proxy.player.play(file, id)
        log('Select ' + file)

    def add(self, file):
        """Universal add file"""
        if os.path.isdir(file):
            self.add_dir(file)
        else:
            self.add_file(file)

        self.sync_songlist()

    def load_cue(self, file):
        '''
        Return cue parse result of file. 
        If cue file doesn't exist or wrong format, return None
        '''
        if not os.path.isfile(file):
            log('File not found: ' + file)
            return None

        if file in self.cds:
            log('Cache found: ' + file)
            return self.cds[file]
        name, ext =  os.path.splitext(file)
        cue_file = name + '.cue'
        cd = Cue(cue_file)
        if cd.tracks: # The format is right
            log('Cue loaded: ' + file)
            cd.file = file
            self.cds[file] = cd
            return cd
        return None

    def add_file(self, file):
        if not self.check_file(file):
            return

        # You can add or drag playlist file directly too
        # Add playlist
        if file.endswith(LP_PLAYLIST_EXT):
            self.load(file)
            return

        log('Add File ' + file)
        name, ext =  os.path.splitext(os.path.basename(file))
        # Add cue files
        if ext.lower() in ['.flac', '.ape', '.ogg']: # Dont check cue file for mp3
            cd = self.load_cue(file)
            if cd:
                self.add_cd(cd)
                return

        # Add rar file`s
        if ext.lower() in ['.rar']:
            p = compress.mount_compressed(file)
            if not p:
                return 
            self.add_dir(p) # Add the uncompressed directory, it's so beautiful!
            return

        # Add plain files
        song = {}
        song['title'] = to_utf8(name)
        song['type'] = 'file'
        song['path'] = file
        song['artist'] = ''
        self.songlist.append(song)

    def add_dir(self, dir):
        log('Add Dir ' + dir)
        for f in sorted(os.listdir(dir)):
            self.add(os.path.join(dir, f))
    
    def add_cd(self, cd):
        for track in cd.tracks.keys():
            self.add_track(cd, track)

    def add_track(self, cd, track):
        if track in cd.tracks:
            log('Add track %d of %s' % (track, cd.file))
            meta  = cd.tracks[track]
            meta['path'] = cd.file
            meta['type'] = 'track'
            meta['track'] = track
            meta['artist'] = meta['performer']
            self.songlist.append(meta)

    def load(self, config_file):
        if not os.path.isfile(config_file):
            return

        # Only support latest config file
        try:
            config = json.loads(open(config_file, 'r').read())
        except ValueError:
            return

        if config['version'] < 3:
            return

        vol = config['volume']
        self.proxy.player.volume = vol
        self.proxy.player.volume_view.set_value(vol / 100.0)

        self.songlist = []
        for song in config['songlist']:
            # Check for not exsits files and update cues
            # If in mem files, do not check
            if compress.MARKER in song['path']:
                self.songlist.append(song)
                continue

            if not os.path.exists(song['path']):
                continue

            if song['type'] == 'file':
                self.songlist.append(song)

            if song['type'] == 'track':
                cd = self.load_cue(song['path'])
                if cd:
                    self.add_track(cd, song['track'])

        self.sync_songlist()

    def save(self, config_file):
        #file = os.path.expanduser(file)
        f = open(config_file, 'w+')
        config = {}
        config['version'] = 3
        config['volume'] = self.proxy.player.volume
        config['songlist'] = self.songlist
        f.write(json.dumps(config))
        f.close()
        log('Playlist %s saved' % config_file)
 

class Player:

    def __init__(self, proxy):
        
        self.proxy = proxy

        self.tooltips = gtk.Tooltips()
        self.timer_enable = False
        view = gtk.VBox(False, 0)

        # Time info and meta
        hbox = gtk.HBox(False, 0)
        self.meta_pos_view = gtk.Label()
        self.meta = gtk.Label()
        hbox.pack_start(self.meta_pos_view, False, False, 1)
        hbox.pack_start(self.meta, False, False, 1)
        view.pack_start(hbox, False, False, 1)

        # Process bar,  assume data is $name, view is $name_view
        self.progress = gtk.Adjustment(0.0, 0.0, 101.0, 0.001, 1.0, 1.0)
        self.progress.connect("value_changed", self.progress_value_changed)
        self.progress_view = gtk.HScale(self.progress)
        self.progress_view.set_draw_value(False)
      
        # For callback handler, we name it as $object_$event
        self.progress_view.connect('button-release-event', self.progress_view_button_release_event)
        self.progress_view.connect('button-press-event', self.progress_view_button_press_event)

        self.volume_view = gtk.VolumeButton()
        self.volume_view.connect('value_changed', self.change_volume)
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(self.progress_view, True, True, 1)
        hbox.pack_start(self.volume_view, False, False, 1)
        view.pack_start(hbox, False, False, 1)
 
        # Control buttons 
        hbox = gtk.HBox(False, 0)
        def controll_button(name, tip):
            button = gtk.ToolButton(getattr(gtk, 'STOCK_MEDIA_%s' % name.upper()))
            hbox.pack_start(button, False, False, 1)
            self.tooltips.set_tip(button, tip)
            button.connect('clicked', self.controll_button_callback, name)
            # Save a reference here, we need to change 'play' button when double click to play
            setattr(self, 'cb_' + name, button)
        
        #controll_button('previous', '上一首')
        controll_button('next', '下一首')
        controll_button('play', '播放')
        controll_button('stop', '停止')
        
        # Check boxes for play mode
        def check_box(name, tip):
            button = gtk.CheckButton(name)
            self.tooltips.set_tip(button, tip)
            hbox.pack_end(button, False, False, 1)
            button.connect("toggled", self.check_box_callback, name)

        check_box('R', '单曲重复')
        check_box('L', '循环播放')
        check_box('S', '乱序播放')

        view.pack_start(hbox, False, False, 1)
        self.view = view

        # Create a idle player 
        self.slave = MPlayerSlave()
        self.slave.debug = self.proxy.debug_view
        self.timer = None

        self.error = False

        # song id of now playing
        self.id = None
        self.idle = True
        self.R_mode = False
        self.S_mode = False
        self.L_mode = False

        # Set default volume
        self.volume = 70
        self.volume_view.set_value(self.volume / 100.0)

        
    def change_volume(self, w, d):
        self.volume = int(w.get_value() * 100)
        self.slave.send('volume %d 1' % self.volume)

    def error_check(self):
        '''Check to see if we have pending errors to read, mainly for detecting wrong mp3 length
           unexpect file ending, file is shorter than the length in meta data
        '''
        fd = self.slave.mplayer.stdout
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)
        while True:
            try:
                line = self.slave.mplayer.stdout.readline()
                if 'Cannot sync MAD frame' in line:
                    log('Found: Cannot sync MAD frame, length meta maybe wrong, or unexpected EOF')
                    self.error = True # Alert main thread there is a error found!
            except IOError:
                break
        fcntl.fcntl(fd, fcntl.F_SETFL, flags)

    def get_length_by_mp3info(self, path):
        try:
            cmd = 'mp3info -p "%%S" %s' % escape_path(path)
            log('Using mp3info to detect length: %s' % cmd)
            tmp = int(commands.getoutput(cmd))
        except:
            return None
        return tmp

    def play(self, file, id):
        log('playing %s %s' % (file, id))
        self.id = id
        # Start playing a new song
        if self.timer:
            gobject.source_remove(self.timer) # Remove old timer

        # Uncompressing if needed
        if compress.MARKER in file:
            if not compress.mount_compressed(compress.get_real_path(file)):
                return

        if not os.path.isfile(file):
            log(file + 'not exists, play next')
            self.play_next()
            return

        self.idle = False

        self.index = 0 # Offset for track file
        self.meta_pos = 0

        song = self.proxy.playlist_view.songlist[id]
        title, artist = song['title'], song['artist']

        # Deal with special chars in shell command, yes, it's ugly but very effective
        self.timer = gobject.timeout_add(1000, self.timer_callback, self) # Start a new one
        self.error = False

        if song['type'] == 'file':
            self.slave.send('loadfile %s\nvolume %d 1' % (escape_path(song['path']), self.volume))

        if song['type'] == 'track':
            log('Play track %d' % song['track'])
            self.index = song['index']
            # We need the function of playing from offset index, but mplayer doesn't provide it
            # 'pausing loadfile' doesn't work in idle slave mode
            self.slave.send('loadfile %s\nseek %d 2' % (escape_path(song['path']), self.index))
            # Mplayer can't seek to the exact offset, so we sleep for a while
            if song['track'] != 0:
                time.sleep(1)
            self.slave.send('volume %d 1' % self.volume)

        self.timer_enable = True

        # Get info, meta data has been converted to utf8 already
        meta = self.slave.get_meta()
        if meta == None:
            log('Bad format ' + file)
            self.play_next()
            return

        # Adjust length
        if song['type'] == 'file':
            self.meta_total = meta['length']
            l = self.get_length_by_mp3info(song['path'])
            if l:
                self.meta_total = l
        if song['type'] == 'track':
            if song['length'] == -1: # Final track
                self.meta_total = int(meta['length'] - self.index)
            else:
                self.meta_total = song['length']

        self.meta_pos_view_update()
        if not title:
            title = os.path.splitext(os.path.basename(song['path']))[0]
        self.meta.set_label('%s %s' % (title, meta['bitrate']))
        self.tooltips.set_tip(self.meta, '%s-%s' % (artist, meta['album']))
        self.set_cb_state(self.cb_play, 'pause')

        # Scroll playlist
        self.proxy.playlist_view.treeview.set_cursor(id)

        # Show lyric
        log('ar: %s ti: %s' % (artist, title))
        ar = normalize_name(artist)
        ti =  normalize_name(title)
        log('I guess it\'s ar: %s ti: %s' % (ar, ti))

        self.proxy.lyric_view.keywords_view.set_text(ar + ' ' + ti)
        self.proxy.lyric_view.curr_ar = ar
        self.proxy.lyric_view.curr_ti = ti
        self.proxy.lyric_view.download_links = None
        self.proxy.lyric_view.show_lyric()

    def play_stop(self):
        # Clear time info, meta, pbar
        self.timer_enable = False
        #self.slave.send('stop')
        self.progress.set_value(0)
        self.meta_pos_view.set_label('')
        self.meta.set_label('')
        self.set_cb_state(self.cb_play, 'play')

    def controll_button_callback(self, widget, data):
        if data is 'stop':
            log(data)
            # Cmd 'stop' won't work, and seek large file to end cost too much
            # So just play a little trick here.
            # It's the pay for being a frontend. You can easily stop playing and do other control stuffs
            # if you are using decoder of your own
            self.slave.send('loadfile no_such_file')
            self.idle = True
            self.play_stop()

        if data is 'next':
            log(data)
            self.play_next()

        if data is 'play':
            status = widget.get_stock_id()
            if status== 'gtk-media-play':
                log('play')
                if self.idle:
                    self.play_next()
                else:
                    self.timer_enable = True
                    self.slave.send('pause') # Start play. When mplayer slave is idle, no effect 
                self.set_cb_state(self.cb_play, 'pause')
            else:
                log('pause')
                self.timer_enable = False
                self.slave.send('pause') # Pause
                self.set_cb_state(self.cb_play, 'play')
        
    def set_cb_state(self, cb, state):
        cb.set_stock_id('gtk-media-' + state)
        tip = {
        'play': '播放',
        'pause':'暂停'
        }
        self.tooltips.set_tip(cb, tip[state])

    def check_box_callback(self, widget, data):
        name = data +'_mode'
        value = widget.get_active()
        log('%s %s' % (name, ('off', 'on')[value]))
        setattr(self, name, value)

    def format_seconds(self, sec):
        return '%02d:%02d' % (sec/60, sec%60)

    def meta_pos_view_update(self):
        self.meta_pos_view.set_text('%s/%s' %(self.format_seconds(self.meta_pos), self.format_seconds(self.meta_total)))

    def progress_value_changed(self, data):
        if self.idle: # If there are no song to play, no effect
            return
        # Only update time info when seeking
        if not self.timer_enable:
            self.meta_pos = int(self.progress.get_value() / 100 * self.meta_total)
            self.meta_pos_view_update()

    def progress_view_button_release_event(self, event, data):
        if self.idle:
            return
        log('Seek end')
        # Re enable timer
        self.set_cb_state(self.cb_play, 'pause')
        self.timer_enable = True
        self.slave.send('seek %d 2' % (self.meta_pos + self.index))

    def progress_view_button_press_event(self, event, data):
        log('Seek begin')
        # Disable timer while seeking
        self.timer_enable = False

    def timer_callback(self, p):
        start = gobject.get_current_time()
        """one second timer callback"""
        if not self.timer_enable:
            return True
        self.meta_pos += 1
        self.error_check()
        if self.meta_pos >= self.meta_total or self.error:
            self.play_next()
            return False
        self.progress.set_value(float(self.meta_pos) / self.meta_total * 100)
        self.meta_pos_view_update()
        self.proxy.lyric_view.scroll_lyric(self.meta_pos)

        end = gobject.get_current_time()
        losttime = int((end - start) * 1000)
        # We have lost some time
        self.timer = gobject.timeout_add(1000 - losttime, self.timer_callback, self) # Start a new one
        return False
    
    def play_next(self):
        # Choose the next song to play
        # If has nothing to play, then stop
        self.play_stop()
        
        total = len(self.proxy.playlist_view.songlist)
        # Repeat mode
        if self.R_mode:
            next = self.id
        else:
            # Shuffle mode
            if self.S_mode:
                random.seed(time.time())
                next = random.randint(0, total - 1)
            else:
                # Sequent mode
                next = self.id
                if next == None:
                    next = 0
                else:
                    next += 1
                # We are at the end of playlist, check if loop 
                if next >= total:
                    if self.L_mode:
                        next = 0 # Loop again
                    else:
                        next = None # Done, stop

        # Becareful here, if next=0, it's still valid, so we don't use 'if next:' here
        if next != None:
            self.play(self.proxy.playlist_view.songlist[next]['path'], next)
        else:
            self.idle = True
        
class Controller:

    def delete_event(self, widget, event, data=None):
        # Save playlist 
        default_dir = os.path.dirname(self.default_playlist)
        if not os.path.isdir(default_dir):
            os.mkdir(default_dir)
        self.playlist_view.save(self.default_playlist)

        if self.player.timer:
            gobject.source_remove(self.player.timer)
            self.player.timer = None

        self.player.slave.send('quit')
        gtk.main_quit()
        return False

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(LP_NAME)
        self.window.connect("delete_event", self.delete_event)
        self.window.set_size_request(225, 400)
        self.window.set_position(gtk.WIN_POS_CENTER)

        self.tooltips = gtk.Tooltips()
        vbox = gtk.VBox(False, 0)
 
        # Debug window
        self.debug_view = debug_view
        debug_view.proxy = self
        
        # Create Menu bar 
        self.menu = Menu(self)
        self.window.add_accel_group(self.menu.accelgroup)
        vbox.pack_start(self.menu.menubar, False, False, 1)
        
        # Player
        self.player = Player(self)
        vbox.pack_start(self.player.view, False, False, 1)


        # PlayList
        self.playlist_view = PlayListView(self)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.playlist_view.treeview)
        vbox.pack_start(sw, True, True, 1)

        # Create a separate Lyric window
        self.lyric_view = LyricView(self)
        x, y = self.window.get_position()
        self.lyric_view.window.move(5 + x + LP_WIDTH, y)
        self.lyric_view.window.show()
        self.menu.change_state('Lyric', True)

        vbox.show()
        self.window.add(vbox)
        self.window.show_all()

        # Load configuration
        self.load_conf()

    def load_conf(self):
        self.default_playlist = os.path.expanduser(LP_PLAYLIST_DEFAULT_FILE)
        self.playlist_view.load(self.default_playlist)

gtk.gdk.threads_init()
debug_view = DebugWindow()

gtk.gdk.threads_enter()
lp = Controller()
gtk.main()
gtk.gdk.threads_leave()

