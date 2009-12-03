
import os
import commands

import util

SHM_ROOT = '/dev/shm/lpad'
MARKER = '.lpad.marker'

def check_support():
    # Check if we have shm and unrar support
    if not commands.getoutput('which unrar'):
        return False
    if not os.path.exists('/dev/shm'):
        return False
    return True

def get_shm_path(f):
    """Return the uncompressed direcoty in memory"""
    f = f[1:] # Get rid of '/'
    return os.path.join(SHM_ROOT, f + MARKER)

def get_real_path(p):
    """Return the real file path in file system"""
    if not p.startswith(SHM_ROOT):
        return None
    return p[len(SHM_ROOT):].split(MARKER)[0]

def mount_compressed(f):
    """Mount rar file to memory, and return the mounted directory"""

    if not check_support():
        return None # Do nothing

    p = get_shm_path(f)
    if os.path.exists(p): # Already uncompressed
        return p

    util.mkdir_p(p)
    tmp = os.getcwd()
    try:
        os.chdir(p)
        os.system('unrar e %s' % util.escape_path(f))
    except:
        pass
    os.chdir(tmp)

    cmd = 'echo %s >> %s' % (util.escape_path(p), os.path.join(SHM_ROOT, 'history'))
    os.system(cmd)

    return p
