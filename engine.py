#encoding: utf8

import os
import re
import urllib, urllib2
from misc import *

class Engine:

    def remove_tags(self, html):
        return re.sub('<.*?>', '', html)

    def search_lrc(self, artist, title):
        """Search lyrics by artist and title, return links of lyric files"""
        url = self.get_search_url(artist, title)
        print url
        try:
            f = urllib2.urlopen(url)
        except urllib2.URLError:
            print 'urlopen error'
            return None
        return self.get_lrc_links(f.read())
    
class BaiduEngine(Engine):

    def get_search_url(self, artist, title):
        params = urllib.urlencode({'wd': ' '.join([to_gb2312(title), to_gb2312(artist), 'filetype:lrc']), 'cl': 3})
        return  'http://www.baidu.com/s' + '?' + params

    def get_lrc_links(self, data):
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

if __name__ == '__main__':
    eng = BaiduEngine()
    print  eng.search_lrc('陈绮贞', '旅行的意义')
