#!/usr/bin/env python

# example treeviewcolumn.py

import pygtk
import os
pygtk.require('2.0')
import gtk
import glob

LP_NAME = 'ListenPad v0.1' 
LP_WIDTH = 225
LP_HEIGHT = 400
"""
class Controller(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.setWindowTitle(LP_NAME)
        self.resize(LP_WIDTH, LP_HEIGHT)
        self.center()

        # Menu
        self.exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        self.exit.setShortcut('Ctrl+Q')
        self.connect(self.exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        
        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(self.exit)


        self.statusBar().showMessage('Ready')

        # Playlist
        self.playlist = QtGui.QListView()
        #layout = QtGui.QVBoxLayout()
        #layout.addWidget(self.playlist) 
        #self.setLayout(layout)

        self.playlist.addColumn('ID')
        self.playlist.addColumn('Name')



    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size =  self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    def closeEvent(self, event):
        # Save config
        pass



app = QtGui.QApplication(sys.argv)
widget = Controller()
widget.show()
sys.exit(app.exec_())
"""

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
        self.uimanager = gtk.UIManager()
        self.accelgroup = self.uimanager.get_accel_group()

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

        self.uimanager.add_ui_from_string(self.ui)
        self.menubar = self.uimanager.get_widget('/MenuBar')

    def OnQuit(self, event):
        gtk.main_quit()

    def OnAddDir(self):
        pass

    def OnClear(self):
        pass

    def OnAbout(self):
        pass

class Controller:

    # Save config here
    def delete_event(self, widget, event, data=None):
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

        self.menu = Menu()
        self.window.add_accel_group(self.menu.accelgroup)

        vbox = gtk.VBox(False, 0)
        vbox.pack_start(self.menu.menubar, False, False, 1)
        vbox.pack_start(self.treeview, False, False, 1)
        vbox.show()

        self.window.add(vbox)
        self.window.show_all()

lp = Controller()
gtk.main()
