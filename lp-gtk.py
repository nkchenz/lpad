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

class Controller:

    # Save config here
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False


    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_title(LP_NAME)
        self.window.connect("delete_event", self.delete_event)

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


        #self.column_id.set_attributes(self.cell_id, text=0)

        # make treeview searchable
        self.treeview.set_search_column(0)

        # Allow sorting on the column
        self.column_name.set_sort_column_id(0)

        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)

        self.window.add(self.treeview)

        self.window.show_all()

lp = Controller()
gtk.main()
