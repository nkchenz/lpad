#!/usr/bin/python
#encoding: utf8
"""
MPlayerSlave: Python binding for mplayer slave mode
CopyRight (C) 2008 Chen Zheng <nkthunder@gmail.com> 

Distributed under terms of GPL v2
"""
import subprocess
import os

MPLAYER_CMD = 'mplayer -slave -quiet -idle  -ao alsa '

class MPlayerSlave(object):
    """
    Audio related commands implemented only, for video I do not have a 
    plan yet
    
    Examples:

        
    SLAVE MODE PROTOCOL
    http://www.mplayerhq.hu/DOCS/tech/slave.txt
    """

    def __init__(self):
        # Create a mplayer slave, wait in idle mode when no songs to play. 
        PIPE = -1
        self.mplayer = subprocess.Popen(MPLAYER_CMD, shell = True, stdin = PIPE, stdout = PIPE, stderr = PIPE, bufsize = 1)
        self.debug = None

    def log(self, s):
        if self.debug:
            self.debug.log(s)
        else:
            print s

    def command(self, cmd):
        #Dont expect for output, because some cmds have no output at all
        self.log(cmd)
        return self.mplayer.stdin.write(cmd +'\n')

    def get_meta(self):
        """
        Get meta infos of current audio playing, return a dict 
        
        get_audio_bitrate
        ANS_AUDIO_BITRATE='192 kbps'
        get_audio_codec
        ANS_AUDIO_CODEC='mad'
        get_audio_samples
        ANS_AUDIO_SAMPLES='44100 Hz, 2 ch.'
        get_meta_album
        ANS_META_ALBUM='F.I.R.�ɶ�����'
        get_meta_artist
        ANS_META_ARTIST='F.I.R.'
        get_meta_comment
        ANS_META_COMMENT='                            '
        get_meta_title
        ANS_META_TITLE='���ǵİ�'
        get_percent_pos
        ANS_PERCENT_POSITION=85
        get_time_length
        ANS_LENGTH=287.00
        """
        meta = {
            'bitrate': self.get_var('audio_bitrate'),
            'codec': self.get_var('audio_codec'),
            'samples': self.get_var('audio_samples'),

            'album': self.get_var('meta_album'),
            'artist': self.get_var('meta_artist'),
            'comment': self.get_var('meta_comment'),
            'title': self.get_var('meta_title'),
            'length': int(float(self.get_var('time_length', 'LENGTH'))),
            }

        # Change gb2312 to utf8
        for k, v in meta.items():
            try:
                v = v.decode('gb2312').encode('utf8')
                meta[k] = v
            except:
                pass
            self.log('%s=%s' % (k, v))

        return meta 

    # mute, pause, quit, stop, 
    # seek seconds 2

    def send(self, cmd):
        # Send cmd to mplayer
        self.command(cmd)

    def get_var(self, var, name = None):
        # Output format: ANS_META_ARTIST='F.I.R.', return the value of var
        #   get_meta_artist
        #   ANS_META_ARTIST='F.I.R.
        #   get_time_length
        #   ANS_LENGTH=287.00
        # Normally, cmd is get_$var, var name in output is ANS_$var.upper().
        # But if it's irregular, you must specify name explicitly.
        cmd = 'get_' + var
        varname = 'ANS_'
        self.command(cmd)
        if name:
            varname += name
        else:
            varname += var.upper()
        while True:
            line = self.mplayer.stdout.readline()
            if line.startswith(varname + '='):
                return line.split('=', 1)[1].strip('\' \n')

if __name__ == '__main__':
    m = MPlayerSlave() 
    print 'hello'
    import time
    m.send('loadfile /chenz/music/fir.mp3')
    time.sleep(3)
    
    print m.get_var('percent_pos', 'PERCENT_POSITION')
    print m.get_var('meta_artist')
    m.send('pause')
    time.sleep(5)
    m.send('pause')
    print m.get_meta()

    time.sleep(10)
    m.send('quit')

