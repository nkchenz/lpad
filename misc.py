#coding: utf8

import re

def to_utf8(s):
    return to_en(s, 'utf8')

def to_gb2312(s):
    return to_en(s, 'gb2312')

def to_en(s, en):
    encodings = ['utf8', 'gb2312', 'gbk', 'big5', 'gb18030', 'cp950']

    for a in encodings:
        try:
            return s.decode(a).encode(en)
        except:
            pass

    return s

def normalize_name(name):
    """Remove links, (*) in name, so we have more chances to hit while searching"""
    new = []
    keywords = ['http', 'www.', '.com', '.cn']
    for a in name.split():
        found = 0
        for k in keywords:
            if k in a:
                found = 1
                break
        if found:
            continue
        new.append(a)
    tmp = ' '.join(new)

    # Remove contents in ()
    remove_patterns = ['\(.*?\)', '\[.*?\]']
    for p in remove_patterns:
        tmp = re.sub(p, '', tmp) 

    # Special chars
    special_chars = ['・', '/']
    for c in special_chars:
        tmp = re.sub(c, '', tmp)
    return tmp.strip() 

def escape_path(file):
    file = file.replace('\'', '\\\'')
    return '\'%s\'' % file

def get_string(input):
    '''read a string, strip and encode it with utf8, remove extra \'"\' '''
    s = to_utf8(input.strip())
    if s[0] == '"':
        s = s[1:]
    if s[-1] == '"':
        s = s[:-1]
    return s
