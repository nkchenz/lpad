#coding: utf8

'''
Cue file Parser
'''

import os
from misc import *

class Cue:
    
    def __init__(self, file):
        self.tracks = {} 
        self.file = ''
        if not os.path.isfile(file):        
            return
        track = {'indexs': [], 'performer': ''} 
        track_no = None
        last_track = None
        for line in open(file).readlines():
            line = line.strip()
            # Found a new track
            if line.startswith('TRACK'):
                if track_no:
                    self.tracks[track_no] =  track
                    last_track = track # Save last track, need to compute its length
                    track = {'indexs': [], 'performer': ''} 
                track_no = int(line.split()[1])
                continue

            if line.startswith('TITLE'):
                t = get_string(line[6:])
                if track_no and not t:
                    t = 'Track %d' % track_no
                track['title'] = t
                continue

            if line.startswith('PERFORMER'):
                track['performer'] = get_string(line[10:])
                continue

            if line.startswith('INDEX'):
                _, id, time = line.split()
                min, sec, f = time.split(':')
                index = int(min) * 60 + float(sec + '.' + f)
                track['indexs'].append(index)
                
                if id == '01':
                    # INDEX 01 is start of this track, 00 is end of last track
                    last_track_end = track['indexs'][0]
                    track['index'] = track['indexs'][0]
                    if len(track['indexs']) == 2: # Have both 00 and 01
                        track['index'] = track['indexs'][1]
                    # Compute length of last track
                    if last_track:
                        last_track['length'] = int(last_track_end - last_track['index'])
                continue

        if track_no:
            track['length'] = -1 # Unfortunately we have no way to get length of the final track
            self.tracks[track_no] = track


if __name__ == '__main__':
    # http://en.wikipedia.org/wiki/Cue_sheet_(computing)
    cd = Cue('test.cue')  
    for k,v in cd.tracks.items():
        print k, v
    '''
    ideer@ideer:/home/chenz/code/ListenPad$ python cue.py
    1 {'index': 0, 'length': 402, 'performer': 'Faithless', 'title': 'Reverence'}
    2 {'index': 402, 'length': 252, 'performer': 'Faithless', 'title': "She's My Baby"}
    3 {'index': 654, 'length': 370, 'performer': 'Faithless', 'title': 'Take The Long Way Home'}
    4 {'index': 1024, 'length': 520, 'performer': 'Faithless', 'title': 'Insomnia'}
    5 {'index': 1544, 'length': 306, 'performer': 'Faithless', 'title': 'Bring The Family Back'}
    6 {'index': 1850, 'length': 454, 'performer': 'Faithless', 'title': 'Salva Mea'}
    7 {'index': 2304, 'length': 251, 'performer': 'Faithless', 'title': 'Dirty Old Man'}
    8 {'index': 2555, 'length': -1, 'performer': 'Faithless', 'title': 'God Is A DJ'}
    '''
