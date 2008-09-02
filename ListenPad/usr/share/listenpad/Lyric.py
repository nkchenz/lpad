#encoding: utf8

import os.path
import re
import urllib, urllib2
from misc import *

class LyricRepo(object):
    
    def __init__(self, path):
        self.path = os.path.expanduser(path)
        self.search_engine = 'http://www.baidu.com/s'
        pass

    def get_path(self, artist, title):
        # Because we find lyrics by artist and title, but there are many songs which do not have these tags
        if not artist:
            artist = '未知'
        return os.path.join(self.path, '%s/%s.lrc' % (artist, title))

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


    def search_lrc(self, artist, title):
        params = urllib.urlencode({'wd': ' '.join([to_gb2312(title), to_gb2312(artist), 'filetype:lrc']), 'cl': 3})
        url = self.search_engine + '?' + params
        print url
        try:
            f = urllib2.urlopen(url)
        except urllib2.URLError:
            print 'urlopen error'
            return None

        return self.get_lrc_link(f.read())
    
    def remove_tags(self, html):
        return re.sub('<.*?>', '', html)

    def get_lrc_link(self, data):
        """Find all the links in search results"""
        links = []
        for line in data.splitlines():
            line = to_utf8(line)

            CHARS = '.*?'
            VAR = '(%s)' % CHARS
            def MARK(s):
                return CHARS+s+CHARS

            if '【LRC】' in line:
                # Friendly writing for regex
                #    '<table.*?href="(.*?)".*?color.*?>(.*?)<.*?color.*?>(.*?)<.*?<br>'
                reg = '<table$CHARShref="$VAR"$CHARS>$VAR<br>'
                reg = reg.replace('$CHARS', CHARS)
                reg = reg.replace('$VAR', VAR)
                #reg = reg.replace('$1', MARK('color'))
                for item in re.findall(reg, line):
                    ar, ti = '', ''
                    try:
                        ti, ar = self.remove_tags(item[1]).split('-')
                    except:
                        pass
                    links.append((item[0], ti.strip(), ar.strip()))
        return links


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
    #l = lyric.local_lookup('周杰伦', '千里之外')
    l = repo.get_lyric('xry', 'meetu')
    if l:
        for k,v in l['lyrics']:
            print k,v 

    a = '周杰伦'
    t = '千里之外'
    links = repo.search_lrc(a, t)
    data = repo.download_lrc(links[0][0])
    repo.save_lyric(a, t, data)

    l = repo.get_lyric(a, t)
    print l['lyrics']
    #print repo.search_lrc('许茹芸', '泪海')

