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
import glob

import subprocess
import threading

import time
import random

LP_NAME = 'ListenPad v0.1' 
LP_WIDTH = 225
LP_HEIGHT = 400
LP_PLAYLIST_INDEX_WIDTH = 35 
LP_PLAYLIST_NAME_WIDTH = LP_WIDTH  - LP_PLAYLIST_INDEX_WIDTH
LP_PLAYLIST_TEXT = '#17E8F1'
LP_PLAYLIST_BACKGROUND = '#000000'

MPLAYER_CMD = '/usr/bin/mplayer'
MPLAYER_ARGS = ''

# Panel
ID_PLAYLIST = 3
ID_INFO = 4
ID_MENU = 6

# Menu items
ID_QUIT = 1
ID_ABOUT = 2
ID_ADD = 7
ID_CLEAR = 8

class PlayList(wx.ListCtrl):
    def __init__(self, parent, id):
        wx.ListCtrl.__init__(self, parent, style = wx.LC_REPORT)
        self.parent = parent
        self.parent.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect)
        self.InsertColumn(0, 'ID', width = LP_PLAYLIST_INDEX_WIDTH)
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
        self.mode_random = False
        self.mode_single_repeat = False
        self.mode_list_loop = False 

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
                wx.CallAfter(self.parent.sb.SetStatusText, file)
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
                    self.selected = None
                    continue
                else:
                    
                    if self.mode_single_repeat:
                        continue
                    
                    if self.mode_random:
                        random.seed(time.time())
                        i = random.randint(0, len(pl) - 1)
                    else:
                        # Sequence list loop mode
                        i += 1
                        if i >= len(pl):
                            if self.mode_list_loop:
                                i = 0
                            else:
                                break # No more to play


    def play_and_wait(self, file):    
        self.mplayer = subprocess.Popen([MPLAYER_CMD, MPLAYER_ARGS + file], stdin = -1)
        self.mplayer.wait()


class Menu(wx.MenuBar):
    
    def __init__(self, parent, id):
        wx.MenuBar.__init__(self, id)
        self.parent = parent
        file = wx.Menu()
        file.Append(ID_QUIT, '&Quit')
        self.parent.Bind(wx.EVT_MENU, self.OnQuit, id = ID_QUIT)
        self.Append(file, '&File')

        playlist = wx.Menu()
        playlist.Append(ID_ADD, '&Add Dir')
        self.parent.Bind(wx.EVT_MENU, self.OnAdd, id = ID_ADD)
        playlist.Append(ID_CLEAR, '&Clear')
        self.parent.Bind(wx.EVT_MENU, self.OnClear, id = ID_CLEAR)
        self.Append(playlist, '&PlayList')


        help = wx.Menu()
        help.Append(ID_ABOUT, '&About')
        self.parent.Bind(wx.EVT_MENU, self.OnAboutBox, id=ID_ABOUT)
        self.Append(help, '&Help')
  
    def OnClear(self, envent):
        self.parent.playlist.list = []
        self.parent.playlist.update()
     
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

        # Menu
        self.SetMenuBar(Menu(self, ID_MENU))


        hbox = wx.BoxSizer(wx.VERTICAL)
        infobox = wx.BoxSizer(wx.HORIZONTAL)

        #self.info = wx.StaticText(self, -1, 'Ready')
        #infobox.Add(self.info, 1, wx.ALIGN_LEFT)
        self.iwant = wx.TextCtrl(self, -1)
        self.iwant.AppendText('I want listen ...')
        infobox.Add(self.iwant, 1, wx.ALIGN_CENTER)
        hbox.Add(infobox, 0, wx.ALIGN_TOP | wx.EXPAND, 3)
        
        # Play mode checkboxes
        modebox = wx.BoxSizer(wx.HORIZONTAL)
        self.cb_random = wx.CheckBox(self, -1, 'Random') #,(10, 10))
        self.cb_loop = wx.CheckBox(self, -1, 'Loop') #,(10, 10))
        self.cb_repeat = wx.CheckBox(self, -1, 'Repeat') #,(10, 10))
        wx.EVT_CHECKBOX(self, self.cb_random.GetId(), self.OnModeRandom)
        wx.EVT_CHECKBOX(self, self.cb_loop.GetId(), self.OnModeLoop)
        wx.EVT_CHECKBOX(self, self.cb_repeat.GetId(), self.OnModeRepeat)
        modebox.Add(self.cb_random, 0, wx.ALIGN_RIGHT)
        modebox.Add(self.cb_loop, 0, wx.ALIGN_RIGHT)
        modebox.Add(self.cb_repeat, 0, wx.ALIGN_RIGHT)
        hbox.Add(modebox, 0, wx.ALIGN_TOP | wx.EXPAND, 3)

        # PlayList
        self.playlist = PlayList(self, ID_PLAYLIST)
        hbox.Add(self.playlist, 2, wx.EXPAND | wx.LEFT | wx.ALIGN_TOP, 10)

        # Used for block player thread if there are no songs to play
        self.cond = threading.Condition()

        # Status bar
        self.sb = self.CreateStatusBar()
        self.sb.SetStatusText('Ready')

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

    def OnModeRandom(self, envent=None):
        self.player.mode_random = self.cb_random.GetValue()
        self.cb_loop.SetValue(False)
        self.player.mode_list_loop = False
        self.cb_repeat.SetValue(False)
        self.player.mode_single_repeat = False

    def OnModeLoop(self, envent=None):
        self.player.mode_list_loop = self.cb_loop.GetValue()
        self.cb_random.SetValue(False)
        self.player.mode_random = False
        self.cb_repeat.SetValue(False)
        self.player.mode_single_repeat = False


    def OnModeRepeat(self, envent=None):
        self.player.mode_single_repeat = self.cb_repeat.GetValue()
        self.cb_random.SetValue(False)
        self.cb_loop.SetValue(False)
        self.player.mode_random = False
        self.player.mode_list_loop = False

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

