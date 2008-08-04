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

LP_NAME = 'ListenPad' 
LP_WIDTH = 225
LP_HEIGHT = 400

class Info(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        #self.text = wx.StaticText(self, -1, 'Ready')

class Option(object):
    pass

class LRC(object):
    pass

class PlayList(object):
    pass

ID_QUIT = 1
ID_ABOUT = 2
ID_PLAYLIST = 3


class Controller(wx.Frame):
    """
    mainframe
    """
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(LP_WIDTH, LP_HEIGHT))
        self.info = Info(self, -1)

        menubar = wx.MenuBar()

        file = wx.Menu()
        file.Append(ID_QUIT, '&Quit')
        self.Bind(wx.EVT_MENU, self.MyClose, id = ID_QUIT)
        menubar.Append(file, '&File')
 
        help = wx.Menu()
        help.Append(ID_ABOUT, '&About')
        self.Bind(wx.EVT_MENU, self.OnAboutBox, id=ID_ABOUT)
        menubar.Append(help, '&Help')
        self.SetMenuBar(menubar)

        self.sb = self.CreateStatusBar()
        
        import glob
        self.playlist = glob.glob('/chenz/music/*.mp3')
        print self.playlist

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.list = wx.ListCtrl(self, ID_PLAYLIST, style=wx.LC_REPORT)

        self.list.InsertColumn(0, 'name', -1)
        #self.list.InsertColumn(1, 'place', width=130)
        
        for f in self.playlist:
            index = self.list.InsertStringItem(sys.maxint, os.path.splitext(os.path.basename(f))[0])
            #self.list.SetStringItem(index, 1, i[1])

        hbox.Add(self.list, -1, wx.EXPAND)
        self.SetSizer(hbox)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect, id = ID_PLAYLIST)

        self.mplayer = None
        self.OrigClose = self.Close
        self.Close = self.MyClose

        self.sb.SetStatusText('Ready')
        self.Centre()
        self.Show()

 
    def kill_mplayer(self):
        if self.mplayer and not self.mplayer.poll():
            cmd = 'kill -9 %d' % self.mplayer.pid
            print cmd
            os.system(cmd)

    def OnSelect(self, event):
        self.kill_mplayer()
        index = event.GetIndex()
        file = self.playlist[index]
        self.mplayer = subprocess.Popen(['mplayer', file], stdin = -1, stdout = -1, stderr = -1)
        print self.mplayer.pid

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

    def MyClose(self, envent):
        self.kill_mplayer()
        #save config here
        self.OrigClose()

app = wx.App()
Controller(None, -1, 'ListenPad')
app.MainLoop()

