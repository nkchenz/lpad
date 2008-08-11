#!/usr/bin/env python

# example treeviewcolumn.py

import pygtk
import os
pygtk.require('2.0')
import gtk
import glob
from Lyric import *

LP_NAME = 'ListenPad v0.1' 
LP_WIDTH = 225
LP_HEIGHT = 400

LP_PLAYLIST_TEXT = '#17E8F1'
LP_PLAYLIST_BACKGROUND = '#000000'

class Menu:
    ui = '''<ui>
    <menubar name="MenuBar">
      <menu action="File">
        <menuitem action="Quit"/>
      </menu>
      <menu action="Playlist">
        <menuitem action="AddDir"/>
        <menuitem action="Clear"/>
      </menu>
      <menu action="Help">
        <menuitem action="About"/>
      </menu>
    </menubar>
    </ui>'''
      
    def __init__(self):
        
        # Creat ui, accelerate keys group
        self.uimanager = gtk.UIManager()
        self.accelgroup = self.uimanager.get_accel_group()

        # Bind 'action' in ui define string or file
        self.actiongroup = gtk.ActionGroup(LP_NAME)
        self.actiongroup.add_actions([('File', None, '_File'),
                                 ('Quit', gtk.STOCK_QUIT, '_Quit', None, '', self.OnQuit),
                                 ('Playlist', None, '_Playlist'),
                                 ('AddDir', None, '_Add Dir', None, '', self.OnAddDir),
                                 ('Clear', None, '_Clear', None, '', self.OnClear),
                                 ('Help', None, '_Help'),
                                 ('About', None, '_About', None, '', self.OnAbout),
                                 ])
        self.uimanager.insert_action_group(self.actiongroup, 0)
        
        # Load ui
        self.uimanager.add_ui_from_string(self.ui)
        self.menubar = self.uimanager.get_widget('/MenuBar')

    def OnQuit(self, event):
        # Fixme: we should call the quit function of main window do some clean work
        gtk.main_quit()

    def OnAddDir(self):
        pass

    def OnClear(self):
        pass

    def OnAbout(self):
        pass


class Lyric:

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
        


class Controller:

    def delete_event(self, widget, event, data=None):
        # Save config here
        gtk.main_quit()
        return False


    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(LP_NAME)
        self.window.connect("delete_event", self.delete_event)
        self.window.set_size_request(225, 400)
        self.window.set_position(gtk.WIN_POS_CENTER)

        # PlayList
        self.liststore = gtk.ListStore(str)
        self.treeview = gtk.TreeView(self.liststore)

        files = glob.glob(os.path.join('/chenz/music', '*.mp3'))
        for i in range(len(files)):
            print files[i]
            self.liststore.append([os.path.basename(files[i])])

        self.cell_name = gtk.CellRendererText()
        self.cell_name.set_property('cell-background', 'black')
        self.cell_name.set_property('foreground', LP_PLAYLIST_TEXT)
        self.column_name = gtk.TreeViewColumn('NAME', self.cell_name, text = 1)
        self.column_name.set_attributes(self.cell_name, text=0)

        self.treeview.append_column(self.column_name)

        self.treeview.set_search_column(0)
        self.column_name.set_sort_column_id(0)
        
        # Create Menu bar 
        self.menu = Menu()
        self.window.add_accel_group(self.menu.accelgroup)

        # Add menu and playlist to the main window
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(self.menu.menubar, False, False, 1)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.treeview) 
        vbox.pack_start(sw, True, True, 1)

        # Create Lyric window
        self.lyric_view = Lyric()
        x, y = self.window.get_position()
        self.lyric_view.window.move(5 + x + LP_WIDTH, y)
        self.lyric_view.window.show_all()
        # Get a lyric repo instance
        self.lyric_repo = LyricRepo()
        self.show_lyric('xry', 'meetu')

        vbox.show()
        self.window.add(vbox)
        self.window.show_all()

    def show_lyric(self, artist, title):
        l = self.lyric_repo.get_lyric(artist, title)
        if l == None:
            print 'Lyric not found'
            return
        pos = self.lyric_view.textbuffer.get_start_iter()
        for timestamp, text in l['lyrics']:
            print timestamp, text
            self.lyric_view.textbuffer.insert(pos, timestamp + text)
        

lp = Controller()
gtk.main()
