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
from Queue import Queue
from threading import Thread

LP_NAME = 'ListenPad' 
LP_WIDTH = 225
LP_HEIGHT = 400

ID_QUIT = 1
ID_ABOUT = 2
ID_PLAYLIST = 3
ID_INFO = 4
ID_PLAY_LIST = 5 
ID_MENU = 6

next_playing = Queue(1)

class Info(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        #self.text = wx.StaticText(self, -1, 'Ready')

class Option(object):
    pass

class LRC(object):
    pass

class PlayList(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, style = wx.LC_REPORT, pos = (100, 10))
        self.parent = parent
        self.list = []
        self.parent.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect)
    
    def add_dir(self, dir):
        self.list += glob.glob(os.path.join(dir, '*.mp3'))
        self.update()

    def update(self):
        self.InsertColumn(0, 'Play List', -1)
        for f in self.list:
            print f
            self.InsertStringItem(sys.maxint, os.path.splitext(os.path.basename(f))[0])
            #self.list.SetStringItem(index, 1, i[1])

    def OnSelect(self, event):
        index = event.GetIndex()
        print index
        next_playing.put(index)
        self.parent.player.kill()

class Player(object):

    def __init__(self, parent):
        self.mplayer = None
        self.parent = parent
        self.quit = False    # main threa use this to inform us to quit
 
    def kill(self):
        if self.mplayer and not self.mplayer.poll():
            cmd = 'kill -9 %d' % self.mplayer.pid
            print cmd
            os.system(cmd)
    
    def mainloop(self):
        print 'thread player started', os.getpid()
        while True:
            print 'waiting for q'
            i = next_playing.get(block = True)
            pl = self.parent.playlist.list
            file = pl[i]
            self.parent.playlist.index = i
            self.parent.sb.SetStatusText(file)
            print 'playing ', file
            self._play(file)
            print 'done' 
            if self.quit:
                break
            if next_playing.empty():
                next = i + 1
                if next >= len(pl):
                    next = 0
                next_playing.put(next)

    def _play(self, file):    
        #self.mplayer = subprocess.Popen(['mplayer', file], stdin = -1, stdout = -1, stderr = -1)
        self.mplayer = subprocess.Popen(['mplayer', file], stdin = -1)
        self.mplayer.wait()


class Menu(wx.MenuBar):
    
    def __init__(self, parent, id):
        wx.MenuBar.__init__(self, id)
        self.parent = parent
        file = wx.Menu()
        file.Append(ID_QUIT, '&Quit')
        self.parent.Bind(wx.EVT_MENU, self.OnQuit, id = ID_QUIT)
        self.Append(file, '&File')

        help = wx.Menu()
        help.Append(ID_ABOUT, '&About')
        self.parent.Bind(wx.EVT_MENU, self.OnAboutBox, id=ID_ABOUT)
        self.Append(help, '&Help')

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
        self.info = Info(self, ID_INFO)

        # Menu
        self.SetMenuBar(Menu(self, ID_MENU))
        
        # PlayList
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.playlist = PlayList(self, ID_PLAYLIST)
        hbox.Add(self.playlist, -1, wx.EXPAND)
        self.SetSizer(hbox)

        # Status bar
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText('Ready')

        # MPlayer interface
        self.player = Player(self)
        self.player_thread = Thread(target = self.player.mainloop)
        self.player_thread.setDaemon(True)
        self.player_thread.start() 
        print 'main pid:', os.getpid()

        self.playlist.add_dir('/chenz/music')

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Centre()
        self.Show()

    def OnClose(self, envent=None):
        #save config here
        self.player.quit = True
        self.player.kill()
        self.Destroy()

app = wx.App()
Controller(None, -1, 'ListenPad')
app.MainLoop()

