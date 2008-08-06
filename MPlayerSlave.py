#!/usr/bin/python
#encoding: utf8
"""
MPlayerSlave: Python binding for mplayer slave mode
CopyRight (C) 2008 Chen Zheng <nkthunder@gmail.com> 

Distributed under terms of GPL v2
"""

class MPlayerSlave(object):
    """
    Audio related commands implemented only, for video I do not have a 
    plan yet
    
    Examples:
        

        
    SLAVE MODE PROTOCOL
    http://www.mplayerhq.hu/DOCS/tech/slave.txt
    """

    def __init__(self):
        """
        Create a mplayer slave, wait in idle mode when no songs to play. 

        """

    def command(self, cmd):
        """Run cmd and return output, it's a common interface"""

    def loadfile(self, file):
        """
        Stop current song and start playing a new song
        """

    def get_audio_info(self):
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
        
    def seek_(self, value, type):
        """
        Seek position
            0 is a relative seek of +/- <value> seconds (default).
            1 is a seek to <value> % in the movie.
            2 is a seek to an absolute position of <value> seconds.

        """


    def mute(self, value):
        """
        Tune sound volum
        """
    
    def pause(self):
        """Pause/unpause the playback"""

    def stop(self):
        """Stop playing current file"""

    def get_percent_pos(self):
        """
        Return current percent position of the song
        """

    def quit(self):
        """
        Quit process 
        """
