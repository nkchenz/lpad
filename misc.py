
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



def escape_path(file):
    file = file.replace('\'', '\\\'')
    return '\'%s\'' % file
