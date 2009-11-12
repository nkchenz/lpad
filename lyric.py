#encoding: utf8

import os.path
import re
import urllib, urllib2
from misc import *

class LyricRepo(object):
    
    def __init__(self, path):
        self.path = os.path.expanduser(path)

    def get_path(self, artist, title):
        # Because we find lyrics by artist and title, but there are many songs which do not have these tags
        if not artist:
            artist = '未知'
        return os.path.join(self.path, '%s/%s.lrc' % (artist, title))

    def get_lyric(self, artist, title):
        """Get lyric by artist and title from local repo
        Return dict
        """
        # Find in cache first
        lyric_file = self.get_path(artist, title)
        if os.path.isfile(lyric_file):
            data = open(lyric_file, 'r').readlines()
            return self.parse_lyric(data)
        else:
            # Download from internet
            return None

    def parse_lyric(self, data):
        """Parse lyric file to a dict
        
        'lyrics': [(timestamp, lyric)]
        """
        lyric = {}
        lyrics = {}
        for line in data:
            # Remove comments and blank lines
            if line.isspace() or line.startswith('#'):
                continue

            line = to_utf8(line)

            r = re.search('(\[.*\])(.*)', line)
            if r == None: 
                continue # Format wrong

            timestamps, text = r.groups()

            # Split multi time stamps by blank
            for t in re.findall('(\[.*?\])', timestamps):
                t = t.strip('[]')
                # Parse something like [ar:westlife], [by:foo], [00:12.98]
                k, _, v = t.partition(':') 
                if k.isdigit():
                    lyrics[t] = text # Timestamp
                else:
                    lyric[k] = v # Meta data

        # Sort lyrics
        lyric['lyrics'] = []
        for t in sorted(lyrics.keys()):
            lyric['lyrics'].append((t, lyrics[t]))

        return lyric

    def download_lrc(self, link):
        try:
            f = urllib2.urlopen(link)
        except:
            print 'download error'
            return None
        return f.read()
           
    def save_lyric(self, artist, title, data):
        #self.servers
        #self.local_path
        path = self.get_path(artist, title)
        os.system('mkdir -p ' + escape_path(os.path.dirname(path)))
        f = open(path, 'w+')
        f.write(data)
        f.close()


if __name__ == '__main__':
    repo = LyricRepo('repo')
    l = repo.get_lyric('xry', 'meetu')
    if l:
        for k,v in l['lyrics']:
            print k,v 
