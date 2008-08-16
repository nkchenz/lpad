#encoding: utf8

import os.path
import re


class LyricRepo(object):
    
    def __init__(self, path):
        self.path = path
        pass

    def get_path(self, artist, title):
        # Because we find lyrics by artist and title, but there are many songs which do not have these tags
        if not artist:
            artist = '未知'
        return os.path.join(self.path, '%s/%s.lyc' % (artist, title))

    def get_lyric(self, artist, title):
        """Get lyric by artist and title
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
        """Parse lyric file to a dict which contains a 'lyrics' list and its item are
        tuples of (timestamp, lyric)
        """
        lyric = {}
        lyrics = {}
        for line in data:
            # Remove comments and blank lines
            if line.isspace() or line.startswith('#'):
                continue

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
                    lyrics[t] = text
                else:
                    lyric[k] = v

        # Sort lyrics
        lyric['lyrics'] = []
        for t in sorted(lyrics.keys()):
            lyric['lyrics'].append((t, lyrics[t]))

        return lyric

            
    def download(self, artist, titile):
        #self.servers
        #self.local_path
        pass


if __name__ == '__main__':
    repo = LyricRepo()
    #l = lyric.local_lookup('周杰伦', '千里之外')
    l = repo.get_lyric('xry', 'meetu')
    for k,v in l['lyrics']:
        print k,v 

