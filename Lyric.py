#encoding: utf8

import os.path
import re

LYRIC_PATH = '.'

class Lyric(object):
    
    def __init__(self):
        pass

    def lookup_local(self, artist, title):
        lyric_file = os.path.join(LYRIC_PATH, '%s-%s.lyc' % (artist, title))
        if os.path.isfile(lyric_file):
            data = open(lyric_file, 'r').readlines()
            return data
        else:
            return None

    def parse_lyric(self, data):
        lyric = {}
        scripts = {}
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
                    scripts[t] = text
                else:
                    lyric[k] = v

        # Sort lyrics
        lyric['scripts'] = []
        for t in sorted(scripts.keys()):
            lyric['scripts'].append((t, scripts[t]))

        return lyric

            
    def download(self, artist, titile):
        #self.servers
        #self.local_path
        pass


if __name__ == '__main__':
    lyric = Lyric()
    #l = lyric.local_lookup('周杰伦', '千里之外')
    l = lyric.lookup_local('xry', 'meetu')
    for k,v in lyric.parse_lyric(l)['scripts']:
        print k,v 

