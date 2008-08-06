#!/usr/bin/python
#encoding: utf8
"""
ListenPad -- a simple player just play mp3
CopyRight (C) 2008 Chen Zheng <nkthunder@gmail.com> 

Distributed under terms of GPL v2
"""

import wx
import os
import sys
import subprocess
import glob
import threading

LP_NAME = 'ListenPad v0.1' 
LP_WIDTH = 225
LP_HEIGHT = 400
LP_PLAYLIST_INDEX_WIDTH = 40
LP_PLAYLIST_NAME_WIDTH = LP_WIDTH  - LP_PLAYLIST_INDEX_WIDTH
LP_PLAYLIST_TEXT = '#17E8F1'
LP_PLAYLIST_BACKGROUND = '#000000'

ID_QUIT = 1
ID_ABOUT = 2
ID_PLAYLIST = 3
ID_INFO = 4
ID_PLAY_LIST = 5 
ID_MENU = 6
ID_ADD = 7


class PlayList(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, style = wx.LC_REPORT)
        self.parent = parent
        self.parent.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect)
        self.InsertColumn(0, 'IND', width = LP_PLAYLIST_INDEX_WIDTH)
        self.InsertColumn(1, 'NAME', width = LP_PLAYLIST_NAME_WIDTH)
        self.list = []
    
    # Refresh playlist
    def update(self):
        self.DeleteAllItems()
        for i in range(len(self.list)):
            index = self.InsertStringItem(i, str(i + 1))
            self.SetStringItem(index, 1, os.path.splitext(os.path.basename(self.list[i]))[0])
            self.SetItemBackgroundColour(index, LP_PLAYLIST_BACKGROUND)
            self.SetItemTextColour(index, LP_PLAYLIST_TEXT)

    def add_dir(self, dir):
        files = glob.glob(os.path.join(dir, '*.mp3'))
        self.list += files
        self.update()

    def OnSelect(self, event):
        index = event.GetIndex()
        self.parent.player.selected = index
        self.parent.player.notify()

class Player(object):

    def __init__(self, parent):
        self.mplayer = None  # MPlayer Thread 
        self.parent = parent
        self.quit = False    # Main thread uses this to inform us to terminate
        self.idle = True     # Ready status, no songs playing
        self.selected = None # The index of the song user clicked
 
    def kill(self):
        if self.mplayer and not self.mplayer.poll():
            cmd = 'kill -9 %d' % self.mplayer.pid
            print cmd
            os.system(cmd)
    
    def notify(self):
        """Something happened, we'd better to wakeup from idle or stop playing"""
        if self.idle:
            self.parent.cond.acquire()
            self.idle = False
            self.parent.cond.notify()
            self.parent.cond.release()
        else:
            self.parent.player.kill()
        
        # WE ARE STILL IN THE MAIN THREAD, NO USE HERE
        # Check whether we should quit
        #if self.quit:
        #    # thread exit
        #    sys.exit(0)

    def mainloop(self):
        print 'Player Thread', os.getpid()
        while True:
            # Wait until we got something to play
            print 'IDLE '
            self.parent.cond.acquire() #acquire the lock
            while self.idle:
                self.parent.cond.wait()
            self.parent.cond.release()

            # Awake from sleep, check whether should quit
            if self.quit:
                return

            # Start playing
            i = self.selected
            self.selected = None # It will be changed by user clicking playlist while we're playing
            pl = self.parent.playlist.list
            while True:
                print i
                file = pl[i]
                #self.parent.sb.SetStatusText(file)
                print 'Playing ', file
                self.play_and_wait(file)
                print 'Done' 
                
                # Back from playing, check whether should quit
                if self.quit:
                    return

                # Choose loop  style here
                if self.selected:
                    i = self.selected
                    continue
                else:
                    #if no more to play break
                    i += 1
                    if i >= len(pl):
                        i = 0

    def play_and_wait(self, file):    
        self.mplayer = subprocess.Popen(['mplayer', file], stdin = -1)
        self.mplayer.wait()


class Menu(wx.MenuBar):
    
    def __init__(self, parent, id):
        wx.MenuBar.__init__(self, id)
        self.parent = parent
        file = wx.Menu()
        file.Append(ID_ADD, '&Add Dir')
        file.Append(ID_QUIT, '&Quit')
        self.parent.Bind(wx.EVT_MENU, self.OnQuit, id = ID_QUIT)
        self.parent.Bind(wx.EVT_MENU, self.OnAdd, id = ID_ADD)
        self.Append(file, '&File')

        help = wx.Menu()
        help.Append(ID_ABOUT, '&About')
        self.parent.Bind(wx.EVT_MENU, self.OnAboutBox, id=ID_ABOUT)
        self.Append(help, '&Help')

    
    def OnAdd(self, envent):
        dialog = wx.DirDialog(None, "Which dir do you want to add? Only *.mp3 files will be added")
        if dialog.ShowModal() == wx.ID_OK:
            dir = dialog.GetPath()
            self.parent.playlist.add_dir(dir)

 
    def OnAboutBox(self, event):
        description = """ListenPad is a simple mp3 player"""
        licence = """GPL v2"""
        info = wx.AboutDialogInfo()
        info.SetName('ListenPad')
        info.SetVersion('v0.1')
        info.SetDescription(description)
        info.SetCopyright('(C) 2008 Chen Zheng')
        info.SetWebSite('http://code.google.com/p/listenpad')
        info.SetLicence(licence)
        info.AddDeveloper('Chen Zheng <nkthunder@gmail.com>')
        info.AddDocWriter('')
        info.AddArtist('')
	info.AddTranslator('')
        wx.AboutBox(info)

    def OnQuit(self, envent):
        self.parent.OnClose()



class Controller(wx.Frame):

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(LP_WIDTH, LP_HEIGHT))

        hbox = wx.BoxSizer(wx.VERTICAL)
        infobox = wx.BoxSizer(wx.HORIZONTAL)

        #self.info = wx.StaticText(self, -1, 'Ready')
        #infobox.Add(self.info, 1, wx.ALIGN_LEFT)

        self.iwant = wx.TextCtrl(self, -1)
        self.iwant.AppendText('I want listen ...')
        infobox.Add(self.iwant, 1, wx.ALIGN_CENTER)

        hbox.Add(infobox, 0, wx.ALIGN_TOP | wx.EXPAND, 3)

        # Menu
        self.SetMenuBar(Menu(self, ID_MENU))
        
        # PlayList
        self.playlist = PlayList(self, ID_PLAYLIST)
        hbox.Add(self.playlist, 2, wx.EXPAND | wx.LEFT | wx.ALIGN_TOP, 10)

        # Used for block player thread if there are no songs to play
        self.cond = threading.Condition()

        # Status bar
        #self.sb = self.CreateStatusBar()
        #self.sb.SetStatusText('Ready')

        # MPlayer interface
        self.player = Player(self)
        self.player_thread = threading.Thread(target = self.player.mainloop)
        self.player_thread.start() 

        # Load auto saved list
        self.conf = os.path.expanduser('~/.ListenPad.mp3list')
        tmp = {}
        if os.path.isfile(self.conf):
            execfile(self.conf, {}, tmp)
            if 'playlist' in tmp:
                self.playlist.list = tmp['playlist']
                self.playlist.update()

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.SetSizer(hbox)
        self.Centre()
        self.Show()

    def OnClose(self, envent=None):
        # Save config
        open(self.conf, 'w+').write('playlist = ' + str(self.playlist.list))
        
        # Terminate player thread
        self.player.quit = True
        self.player.notify()

        self.Destroy()

print 'Main Thread ', os.getpid()
app = wx.App()
Controller(None, -1, LP_NAME)
app.MainLoop()

