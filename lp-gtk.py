#!/usr/bin/env python

# example treeviewcolumn.py

import pygtk
import os
pygtk.require('2.0')
import gtk
import glob
from Lyric import *
from MPlayerSlave import *

LP_NAME = 'ListenPad' 
LP_VERSION = 'v0.1'
LP_WIDTH = 225
LP_HEIGHT = 400

LP_PLAYLIST_TEXT = '#17E8F1'
LP_PLAYLIST_BACKGROUND = '#000000'
LP_PLAYLIST_DEFAULT_FILE = '~/.listenpad.list'

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
            ('Help', None, '_Help'),
            ('About', None, '_About', None, '', self.OnAbout),])
        self.uimanager.insert_action_group(self.actiongroup, 0)
        
        # Load ui
        self.uimanager.add_ui_from_string(self.ui)
        self.menubar = self.uimanager.get_widget('/MenuBar')

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

class LyricView:

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(LP_WIDTH * 2, LP_HEIGHT)
        #self.window.set_position(gtk.WIN_POS_CENTER)

        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textview = gtk.TextView()

        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.set_justification(gtk.JUSTIFY_CENTER)

        self.textbuffer = self.textview.get_buffer()
        #self.tag = self.textbuffer.create_tag(name=None, background='#000000', foreground='#0000ff')
        #start = self.textbuffer.get_iter_at_line(0)
        #end = self.textbuffer.get_iter_at_line(-1)
        #self.textbuffer.apply_tag(self.tag, start, end)

        self.sw.add(self.textview)
        self.sw.show()
        self.textview.show()
        
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(self.sw, True, True, 1)
        vbox.show()
        self.window.add(vbox)
        
    def show_lyric(self, lyric):
        pos = self.textbuffer.get_start_iter()
        for timestamp, text in lyric['lyrics']:
            print timestamp, text
            self.textbuffer.insert(pos, timestamp + text)

class PlayListView:
    def __init__(self):
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
        self.treeview.set_search_column(0)
        self.column_name.set_sort_column_id(0)
        self.treeview.set_headers_visible(False)

    def add_file(self, file):
        print 'Add File:', file
        self.liststore.append([file, os.path.basename(file)])

    def add_dir(self, dir):
        print 'Add Dir:', dir
        files = glob.glob(os.path.join(dir, '*.mp3'))
        for i in range(len(files)):
            self.add_file(files[i])

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
 
        
class Controller:

    def delete_event(self, widget, event, data=None):
        # Save playlist 
        self.playlist_view.save(self.default_playlist)
        gtk.main_quit()
        return False


    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(LP_NAME)
        self.window.connect("delete_event", self.delete_event)
        self.window.set_size_request(225, 400)
        self.window.set_position(gtk.WIN_POS_CENTER)

        vbox = gtk.VBox(False, 0)
        
        # Create Menu bar 
        self.menu = Menu(self)
        self.window.add_accel_group(self.menu.accelgroup)
        vbox.pack_start(self.menu.menubar, False, False, 1)

        # PlayList
        self.playlist_view = PlayListView()
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.playlist_view.treeview) 
        vbox.pack_start(sw, True, True, 1)

        # Create Lyric window
        self.lyric_view = LyricView()
        x, y = self.window.get_position()
        self.lyric_view.window.move(5 + x + LP_WIDTH, y)
        self.lyric_view.window.show_all()
        # Get a lyric repo instance
        self.lyric_repo = LyricRepo()

        vbox.show()
        self.window.add(vbox)
        self.window.show_all()

        # Load configuration
        self.load_conf()

    def load_conf(self):
        self.default_playlist = LP_PLAYLIST_DEFAULT_FILE
        self.playlist_view.load(self.default_playlist)
        self.show_lyric('xry', 'meetu')

    def show_lyric(self, artist, title):
        l = self.lyric_repo.get_lyric(artist, title)
        if l == None:
            print 'Lyric not found'
            return
        self.lyric_view.show_lyric(l)
        

lp = Controller()
gtk.main()
