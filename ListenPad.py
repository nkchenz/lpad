#!/usr/bin/env python
#encoding: utf8

# example treeviewcolumn.py

import pygtk
import os
pygtk.require('2.0')
import gtk
import gobject
import pango
import glob
from Lyric import *
from MPlayerSlave import *
import time
import urllib
import random
import threading

from misc import *

LP_NAME = 'ListenPad' 
LP_VERSION = 'v0.1'
LP_WIDTH = 225
LP_HEIGHT = 400

LP_PLAYLIST_TEXT = '#17E8F1'
LP_PLAYLIST_BACKGROUND = '#000000'
LP_PLAYLIST_DEFAULT_FILE = '~/.listenpad.list'

LYRIC_REPO_PATH = '/home/chenz/code/ListenPad/repo'


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
        <menuitem action="Quit"/>
      </menu>
      <menu action="Playlist">
        <menuitem action="AddDir"/>
        <menuitem action="AddFile"/>
        <menuitem action="Clear"/>
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
            ('Quit', gtk.STOCK_QUIT, '_Quit', None, '', self.OnQuit),
            ('Playlist', None, '_Playlist'),
            ('AddDir', None, '_Add Dir', None, '', self.OnAddDir),
            ('AddFile', None, '_Add File', None, '', self.OnAddFile),
            ('Clear', None, '_Clear', None, '', self.OnClear),
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

    def OnDebug(self, event):
        if event.get_active():
            self.proxy.debug_view.window.show_all()
        else:
            self.proxy.debug_view.window.hide()


    def OnLyric(self, event):
        if event.get_active():
            self.proxy.lyric_view.window.show_all()
        else:
            self.proxy.lyric_view.window.hide()

    def OnQuit(self, event):
        # Fixme: we should call the quit function of main window do some clean work
        gtk.main_quit()

    def OnAddDir(self, event):
        dialog = gtk.FileChooserDialog(title='Which dir do you want to add?', \
                    action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,\
                    buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,\
                              gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            dir = dialog.get_filename()
            self.proxy.playlist_view.add_dir(dir)
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
                self.proxy.playlist_view.add_file(f)
        dialog.destroy()

    def OnClear(self, event):
        self.proxy.playlist_view.liststore.clear()

    def OnAbout(self, event):
        about = gtk.AboutDialog()
        infos = {
            'name': LP_NAME,
            'version': LP_VERSION,
            'copyright': '(C) 2008 Chen Zheng',
            'license': 'GPL v2',
            'website': 'http://code.google.com/p/listenpad',
            'authors': ['Chen Zheng <nkthunder@gmail.com>'],
            'comments': 'ListenPad: a light music player for linux',
            }
        for k, v in infos.items():
            name = 'set_' + k
            setter = getattr(about, name)
            setter(v)
        about.run()
        about.hide()

class DebugWindow:
    """
    Debug info window
    """
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
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
        self.window.set_skip_taskbar_hint(True)
        #self.window.show()
        #self.window.hide()
    
    def hide_on_close(self, a, b):
        self.window.hide()
        return True

    def log(self, s):
        pos = self.textbuffer.get_end_iter()
        #self.textbuffer.insert(pos, '%s %s\n' % (time.ctime(), s))
        self.textbuffer.insert(pos, '%s\n' % (s))
        self.textview.scroll_to_iter(self.textbuffer.get_end_iter(), 0, True, 1.0, 0.8) 
 

class LyricView:

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(LP_WIDTH * 2, LP_HEIGHT)        
        self.window.connect("delete_event", self.hide_on_close)
        #self.window.set_position(gtk.WIN_POS_CENTER)

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
        vbox.show()
        self.window.add(vbox)
        #self.window.set_skip_taskbar_hint(True)

        self.repo = LyricRepo(LYRIC_REPO_PATH)
        self.last_line = None

    # Dont care what 'a' 'b' really are
    def hide_on_close(self, a, b):
        self.window.hide()
        return True 

    def scroll_lyric(self, pos):
        # No lyric found
        if not self.lyric:
            return
        i = 0
        for timestamp, text in self.lyric['lyrics']:
            min, sec = timestamp.split(':')
            sec = int(min) * 60 + float(sec)
            if sec >= pos:
                if sec > pos + 1:
                    return # Too early
                break
            i += 1
        self.show_line(i)

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
        self.add_line('Searching from %s' % self.repo.search_engine)
        self.add_line('artist: %s title: %s' % (ar, ti))
        
        links = self.repo.search_lrc(ar, ti)
        if not links:
            self.add_line('Nothing found')
            return

        for link in links:
             self.add_line('href=%s artist=%s title=%s' % (link[0], link[2], link[1]))
        
        href = links[0][0]
        self.add_line('Select ' + href)
        data = self.repo.download_lrc(href)
        if not data:
            self.add_line('Download error')
            return
        
        self.add_line('Saving to ' + self.repo.get_path(ar, ti))
        self.repo.save_lyric(ar, ti, data)
        self.add_line('Done, reloading')        
        time.sleep(2)
        self.show_lyric(ar, ti)
        return False

    def add_line(self, line):
        pos = self.textbuffer.get_end_iter()
        self.textbuffer.insert(pos, line + '\n')
        log(line)

    def show_lyric(self, artist, title):
        # Clear lyric window first
        start, end = self.textbuffer.get_bounds()
        self.textbuffer.delete(start, end)

        l = self.repo.get_lyric(artist, title)
        self.lyric = l
        if l == None:
            log('Lyric not found')
            self.add_line('%s\n没有找到歌词' % self.repo.get_path(artist, title))
            #gobject.idle_add(self.search_internet)
            #se = threading.Thread(target = self.search_internet, args=(artist, title))
            #se.start()
            gobject.timeout_add(10, self.search_internet, artist, title) # Start a new one
            return

        pos = self.textbuffer.get_start_iter()
        log('Show Lyric ' + artist +  title)
        for timestamp, text in l['lyrics']:
            self.textbuffer.insert(pos, timestamp + text)

class PlayListView:
    def __init__(self, proxy):

        self.proxy = proxy # Controller

        # Model of this View, real data
        # the first 'str' is abosolute file path
        self.liststore = gtk.ListStore(str, str) 
        self.treeview = gtk.TreeView(self.liststore)

        style = gtk.CellRendererText()
        style.set_property('cell-background', 'black')
        style.set_property('foreground', LP_PLAYLIST_TEXT)

        # text is index of the item in liststore
        self.column_name = gtk.TreeViewColumn('NAME', style, text = 1)
        self.treeview.append_column(self.column_name)
        self.treeview.set_enable_search(False)
        #self.treeview.set_search_column(0)
        self.column_name.set_sort_column_id(0)
        self.treeview.set_headers_visible(False)
        #self.treeview.set_reorderable(True)

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

            # Multiple delete with  'd'
            if key == ord('d'):
                liststore, items =  self.treeview.get_selection().get_selected_rows()
                # Becare with the indexes after delete 
                i = 0
                for item in items:
                    row = item[0] - i
                    i += 1
                    log('Delete ' + liststore[row][0])
                    del liststore[row]

    def check_file(self, file):
        # If file exists and type is supportted, return True. Else return False
        self.support_types = ['.mp3', '.ape', '.flac', '.ogg']
        return os.path.isfile(file) and os.path.splitext(file)[1] in self.support_types

    def selection(self, path, col, item):
        id = col[0]
        file = self.liststore[id][0]
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

    def add_file(self, file):
        if not self.check_file(file):
            return
        log('Add File ' + file)
        self.liststore.append([file, os.path.splitext(os.path.basename(file))[0]])

    def add_dir(self, dir):
        log('Add Dir ' + dir)
        for f in os.listdir(dir):
            self.add(os.path.join(dir, f))
    
    def load(self, file):
        file = os.path.expanduser(file)
        tmp = {}
        if os.path.isfile(file):
            execfile(file, {}, tmp)
            if 'playlist' in tmp:
                for f in tmp['playlist']:
                    self.add_file(f)

    def save(self, file):
        file = os.path.expanduser(file)
        f = open(file, 'w+')
        plist = []
        for item in self.liststore:
            plist.append(item[0])
        f.write('playlist = ' + str(plist))
        f.close()
 

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
        view.pack_start(self.progress_view, False, False, 1)
       
        # For callback handler, we name it as $object_$event
        self.progress_view.connect('button-release-event', self.progress_view_button_release_event)
        self.progress_view.connect('button-press-event', self.progress_view_button_press_event)

        # Control buttons 
        hbox = gtk.HBox(False, 0)
        def controll_button(name):
            button = gtk.ToolButton(getattr(gtk, 'STOCK_MEDIA_%s' % name.upper()))
            hbox.pack_start(button, False, False, 1)
            button.connect('clicked', self.controll_button_callback, name)
            # Save a reference here, we need to change 'play' button when double click to play
            setattr(self, 'cb_' + name, button) 
        
        controll_button('next')
        controll_button('play')
        controll_button('stop')
        
        # Check boxes for play mode
        def check_box(name, tip):
            button = gtk.CheckButton(name)
            self.tooltips.set_tip(button, tip)
            hbox.pack_end(button, False, False, 1)
            button.connect("toggled", self.check_box_callback, name)

        check_box('R', 'Repeat a single song')
        check_box('L', 'Loop the whole playlist')
        check_box('S', 'Shuffle playing')

        view.pack_start(hbox, False, False, 1)
        self.view = view

        # Create a idle player 
        self.slave = MPlayerSlave()
        self.slave.debug = self.proxy.debug_view
        self.timer = None

        # song id of now playing
        self.id = None
        self.R_mode = False
        self.S_mode = False
        self.L_mode = False

    def play(self, file, id):
        log('playing %s %s' % (file, id))
        self.id = id
        # Start playing a new song
        if self.timer:
            gobject.source_remove(self.timer) # Remove old timer

        # Deal with special chars in shell command, yes, it's ugly but very effective
        self.timer = gobject.timeout_add(1000, self.timer_callback, self) # Start a new one
        self.slave.send('loadfile %s' % escape_path(file))
        self.timer_enable = True

        # Get info
        meta = self.slave.get_meta()
        self.meta_pos = 0
        self.meta_total = meta['length']
        self.meta_pos_view_update()
        title = meta['title']
        if not title:
            title = os.path.splitext(os.path.basename(file))[0]
        self.meta.set_label('%s %s' % (title, meta['bitrate']))
        self.tooltips.set_tip(self.meta, '%s-%s' % (meta['artist'], meta['album']))
        self.cb_play.set_stock_id('gtk-media-pause')

        # Scroll playlist
        self.proxy.playlist_view.treeview.scroll_to_cell((id, 0))

        # Show lyric
        self.proxy.lyric_view.show_lyric(meta['artist'], title)

    def play_stop(self):
        # Clear time info, meta, pbar
        self.timer_enable = False
        #self.slave.send('stop')
        self.progress.set_value(0)
        self.meta_pos_view.set_label('')
        self.meta.set_label('')
        self.cb_play.set_stock_id('gtk-media-play')

    def controll_button_callback(self, widget, data):
        if data is 'stop':
            log(data)
            # Cmd 'stop' won't work, so just seek to the end
            self.slave.send('seek 100 1')
            self.play_stop()

        if data is 'next':
            log(data)
            self.play_next()

        if data is 'play':
            status = widget.get_stock_id()
            if status== 'gtk-media-play':
                log('play')
                self.timer_enable = True
                self.slave.send('pause') # Start play. When mplayer slave is idle, no effect 
                widget.set_stock_id('gtk-media-pause')
            else:
                log('pause')
                self.timer_enable = False
                self.slave.send('pause') # Pause
                widget.set_stock_id('gtk-media-play')
        

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
        # Only update time info when seeking
        if not self.timer_enable:
            self.meta_pos = int(self.progress.get_value() / 100 * self.meta_total)
            self.meta_pos_view_update()

    def progress_view_button_release_event(self, event, data):
        log('Seek end')
        # Re enable timer
        self.timer_enable = True
        self.slave.send('seek %d 2' % self.meta_pos)

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
        #log(self.slave.get_var('percent_pos') +  self.meta_pos)
        if self.meta_pos > self.meta_total: # self.slave.get_var('percent_pos') == '100':
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
        
        total = len(self.proxy.playlist_view.liststore)
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
            self.play(self.proxy.playlist_view.liststore[next][0], next)
        
class Controller:

    def delete_event(self, widget, event, data=None):
        # Save playlist 
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
        self.window.connect("focus-in-event", self.focus_in_event)
        self.window.set_size_request(225, 400)
        self.window.set_position(gtk.WIN_POS_CENTER)

        self.tooltips = gtk.Tooltips()
        vbox = gtk.VBox(False, 0)
 
        # Debug window
        self.debug_view = debug_view
        
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

        # Status bar
        #self.status = gtk.Statusbar()  
        #self.status.show()
        #vbox.pack_start(self.status, False, False, 1)

        # Create a separate Lyric window
        self.lyric_view = LyricView()
        x, y = self.window.get_position()
        self.lyric_view.window.move(5 + x + LP_WIDTH, y)
        #self.lyric_view.window.show_all()
        # Get a lyric repo instance

        vbox.show()
        self.window.add(vbox)
        self.window.show_all()

        # Load configuration
        self.load_conf()

    # Check to see if we need to show these windows
    def focus_in_event(self, widget, e):
        if e.in_:
            pass

    def load_conf(self):
        self.default_playlist = LP_PLAYLIST_DEFAULT_FILE
        self.playlist_view.load(self.default_playlist)   

debug_view = DebugWindow()
lp = Controller()
gtk.main()
