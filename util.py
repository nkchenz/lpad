import os

def mkdir_p(path):
    """mkdir -p """
    try:
        os.makedirs(path)
    except OSError, err:
        if err.errno == 17:
            pass
        else:
            raise

def escape_path(p):
    p = p.replace('\'', '\\\'')
    return '\'%s\'' % p
