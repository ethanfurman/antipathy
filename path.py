"""\
Copyright
=========
    - Copyright: 2011-2014 Ethan Furman
    - Author: Ethan Furman
    - Contact: ethan@stoneleaf.us
    - Version: 0.73.002 as of 2014-06-19

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    - Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    - Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    - The name of the author may not be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import glob as _glob
import os as _os
import shutil as _shutil
import sys as _sys

__all__ = ['Path']

String = (str, unicode)
native_glob = _glob.glob
native_listdir = _os.listdir

SEP = '/'
system_sep = _os.path.sep

pyver = float('%s.%s' % _sys.version_info[:2])

version = 0, 73, 2

class Path(object):
    """\
    vol = [ c: | //node/sharepoint | '' ]
    dirs  = [ / | ./ ] + path/to/somewhere/
    filename  = filename.part1.ext
    base  = filename
    ext   = .part1.ext
    """

    def __new__(cls, string=None, sep=None):
        if string is None:
            raise ValueError("no path specified")
        if isinstance(string, cls):
            return string
        if isinstance(string, str):
            new_cls = sPath
        else:
            new_cls = uPath
        p = new_cls.__new__(new_cls, string, sep=sep)
        return p

methods = {}

def vol(self):
    return self.__class__(self._vol)
methods['vol'] = property(vol)
del vol

def dirs(self):
    return self.__class__(self._dirs)
methods['dirs'] = property(dirs)
del dirs

def path(self):
    return self.__class__(self._path)
methods['path'] = property(path)
del path

def filename(self):
    return self.__class__(self._filename)
methods['filename'] = property(filename)
del filename

def base(self):
    return self.__class__(self._base)
methods['base'] = property(base)
del base

def ext(self):
    return self.__class__(self._ext)
methods['ext'] = property(ext)
del ext

def elements(self):
    return list(self.iter())
methods['elements'] = property(elements)
del elements

def dir_elements(self):
    return list(self.iter_dirs())
methods['dir_elements'] = property(dir_elements)
del dir_elements

def iter_all(self):
    result = list(self.iter_dirs())
    if self.vol:
        result.insert(0, self.vol)
    if self.filename:
        result.append(self.filename)
    return iter(result)
methods['iter'] = iter_all
del iter_all

def iter_dirs(self):
    result = []
    cls = self.__class__
    if self._dirs:
        if self._dirs[0] == SEP:
            result = [cls(SEP)]
        dirs = self._dirs.strip(SEP)
        if dirs:
            result.extend([cls(d) for d in dirs.split(SEP)])
    return iter(result)
methods['iter_dirs'] = iter_dirs
del iter_dirs

def base_cls(self):
    return self.__class__.__base__
methods['base_cls'] = property(base_cls)
del base_cls

def __new__(cls, string='', sep=None):
    new_cls = cls.__bases__[1]  # either str or unicode
    vol = dirs = filename = base = ext = new_cls()
    if sep and sep != SEP:
        string = string.replace(sep, SEP)
    elif system_sep != SEP:
        string = string.replace(system_sep, SEP)
    if string == '.':
        string = './'
    elif string == '..':
        string = '../'
    string = string.rstrip('.')
    sep = SEP
    if string[:2] == sep+sep:           # usually '//'
        pieces = string.split(sep)
        vol = sep.join(pieces[:4])
        pieces = pieces[4:]
        if pieces:
            pieces.insert(0, '')
    elif string[1:2] == ':':
        vol, string = string[:2], string[2:]
        pieces = string.split(sep)
    else:
        vol = ''
        pieces = string.split(sep)
    for bit in pieces[1:-1]:
        if not bit:
            raise ValueError("bad path: %r" % string)
    if pieces:
        if pieces[-1] == '':    # path ended in /
            dirs = sep.join(pieces)
        else:
            dirs = sep.join(pieces[:-1])
            if pieces[:-1]:
                dirs += sep
            filename = pieces[-1]
            ext_start = filename.rfind('.')
            if ext_start != -1:
                base, ext = filename[:ext_start], filename[ext_start:]
            else:
                base = filename
    p = new_cls.__new__(cls, vol + dirs + filename)
    p._vol = vol
    p._dirs = dirs
    p._path = vol + dirs
    p._filename = filename
    p._base = base
    p._ext = ext
    return p
methods['__new__'] = __new__
del __new__

def __add__(self, other):
    if not isinstance(other, String):
        return NotImplemented
    return self.__class__(self._path + self._filename + other)
methods['__add__'] = __add__
del __add__

def __contains__(self, text):
    text = text.replace(system_sep, SEP)
    return text in self._path+self._filename
methods['__contains__'] = __contains__
del __contains__

def __div__(self, other):
    if not isinstance(other, String):
        return NotImplemented
    other = self.__class__(other)
    if other._vol:
        raise ValueError("Cannot combine %r and %r" % (self, other))
    current = self._path + self._filename
    if current[-1:] == SEP:
        current = current[:-1]
    next = other._dirs + other._filename
    if next[:1] == SEP:
        next = next[1:]
    return self.__class__(current + SEP + next)
methods['__div__'] = __div__
methods['__truediv__'] = __div__
del __div__

def __eq__(self, other):
    if not isinstance(other, String):
        return NotImplemented
    other = self.__class__(other)
    return self._path == other._path and self._filename == other._filename
methods['__eq__'] = __eq__
del __eq__

def __hash__(self):
    return (self._path + self._filename).__hash__()
methods['__hash__'] = __hash__
del __hash__

def __mod__(self, other):
    return self.__class__((self._path + self._filename) % other)
methods['__mod__'] = __mod__
del __mod__

def __mul__(self, other):
    if not isinstance(other, String):
        return NotImplemented
    other = self.__class__(other)
    if other._vol:
        raise ValueError("Cannot combine %r and %r" % (self, other))
    vol = self._vol
    current = self._dirs
    next = other._dirs
    if current and next and next[0] == SEP:
            dirs = current + next[1:]
    else:
        dirs = current + next
    new_path = []
    for dir in dirs.split(SEP):
        if dir not in ('.','..'):
            new_path.append(dir)
        elif dir == '..':
            if not new_path or new_path[-1] == '':
                raise ValueError("Too many .. dirs in %s" % dirs)
            new_path.pop()
    dirs = SEP.join(new_path)
    base = self._base + other._base
    ext = self._ext + other._ext
    if vol[:2] == SEP*2 and dirs[:1] != SEP:
        dirs = SEP + dirs
    return self.__class__(''.join([vol, dirs, base, ext]))
methods['__mul__'] = __mul__
del __mul__

def __ne__(self, other):
    return not self == other
methods['__ne__'] = __ne__
del __ne__

def __radd__(self, other):
    if not isinstance(other, String):
        return NotImplemented
    return self.__class__(other + self._path + self._filename)
methods['__radd__'] = __radd__
del __radd__

def __rdiv__(self, other):
    if not isinstance(other, String):
        return NotImplemented
    other = self.__class__(other)
    return other / self
methods['__rdiv__'] = __rdiv__
methods['__rtruediv__'] = __rdiv__
del __rdiv__

def __repr__(self):
    string = self._path + self._filename
    return "Path(%r)" % string
methods['__repr__'] = __repr__
del __repr__

def __rmod__(self, other):
    return other % (self._path + self._filename)
methods['__rmod__'] = __rmod__
del __rmod__ 

def __rmul__(self, other):
    if not isinstance(other, String):
        return NotImplemented
    other = self.__class__(other)
    return other * self
methods['__rmul__'] = __rmul__
del __rmul__

def __rsub__(self, other):
    if not isinstance(other, String):
        return NotImplemented
    other = self.__class__(other)
    return other - self
methods['__rsub__'] = __rsub__
del __rsub__

def __str__(self):
    string = self._path + self._filename
    return string
methods['__str__'] = __str__
del __str__

def __sub__(self, other):
    if not isinstance(other, String):
        return NotImplemented
    other = self.__class__(other)
    o_vol, o_dirs, o_base, o_ext = other._vol, other._dirs, other._base, other._ext
    s_vol, s_dirs, s_base, s_ext = self._vol, self._dirs, self._base, self._ext
    if o_vol:
        if o_vol != s_vol:
            raise ValueError("cannot subtract %r from %r" % (o_vol, s_vol))
        vol = ''
    else:
        vol = s_vol
    if o_dirs:
        if not s_dirs.startswith(o_dirs):
            raise ValueError("cannot subtract %r from %r" % (o_dirs, s_dirs))
        dirs = s_dirs[len(o_dirs):]
    else:
        dirs = s_dirs
    if o_base or o_ext:
        o_filename = o_base + o_ext
        if dirs.startswith(o_filename):
            dirs = dirs[len(o_filename):]
            o_base = o_ext = ''
    if o_base:
        if s_base.startswith(o_base):
            base = s_base[len(o_base):]
        else:
            raise ValueError("cannot subtract %r from %r" % (o_base, dirs + s_base))
    else:
        base = s_base
    if o_ext:
        if s_ext.startswith(o_ext):
            ext = s_ext[len(o_ext):]
        else:
            raise ValueError("cannot subtract %r from %r" % (o_ext, dirs + s_ext))
    else:
        ext = s_ext
    if vol[:2] == SEP*2 and not dirs[:1] == SEP:
        dirs = SEP + dirs
    return self.__class__(vol + dirs + base + ext)
methods['__sub__'] = __sub__
del __sub__

def copy(self, dst):
    'thin wrapper around shutil.copy2'
    if isinstance(dst, self.__class__):
        dst = self.base_cls(dst)
    src = self.base_cls(self)
    _shutil.copy2(src, dst)
methods['copy'] = copy
del copy

def copytree(self, dst, symlinks=False, ignore=None):
    'thin wrapper around shutil.copytree'
    if isinstance(dst, self.__class__):
        dst = self.base_cls(dst)
    src = self.base_cls(src)
    _shutil.copytree(src, dst, symlinks, ignore)
methods['copytree'] = copytree
del copytree

def count(self, sub, start=None, end=None):
    new_sub = sub.replace(system_sep, SEP)
    start = start or 0
    end = end or len(self)
    return (self._path + self._filename).count(new_sub)
methods['count'] = count
del count

def chmod(self, mode):
    "thin wrapper around os.chmod"
    _os.chmod(self, mode)
methods['chmod'] = chmod
del chmod

def chown(self, uid, gid):
    "thin wrapper around os.chown"
    _os.chown(self, uid, gid)
methods['chown'] = chown
del chown

def endswith(self, suffix, start=None, end=None):
    if isinstance(suffix, String):
        new_suffix = suffix.replace(system_sep, SEP)
    else:
        try:
            new_suffix = suffix.__class__([x.replace(system_sep, SEP) for x in suffix])
        except:
            raise TypeError("Can't convert %r to str implicitly" % suffix.__class__)
    start = start or 0
    end = end or len(self)
    return (self._path + self._filename).endswith(new_suffix, start, end)
methods['endswith'] = endswith
del endswith

def exists(self):
    return _os.path.exists(self)
methods['exists'] = exists
del exists

def find(sub, start=None, end=None):
    new_sub = sub.replace(system_sep, SEP)
    start = start or 0
    end = end or len(self)
    return (self._path + self._filename).find(new_sub)
methods['find'] = find
del find

def format(self, other):
    raise AttributeError("'Path' object has no attribute 'format'")
methods['format'] = format
del format

def format_map(self, other):
    raise AttributeError("'Path' object has no attribute 'format_map'")
methods['format_map'] = format_map
del format_map

def glob(self):
    return [Path(p) for p in native_glob(self)]
methods['glob'] = glob
del glob

def index(self, sub, start=None, end=None):
    result = self.find(sub, start, end)
    if result == -1:
        raise ValueError('substring not found')
methods['index'] = index
del index

def isdir(self):
    return _os.path.isdir(self)
methods['isdir'] = isdir
del isdir

def isfile(self):
    return _os.path.isfile(self)
methods['isfile'] = isfile
del isfile

def islink(self):
    return _os.path.islink(self)
methods['islink'] = islink
del islink

def ismount(self):
    return _os.path.ismount(self)
methods['ismount'] = ismount
del ismount

def listdir(self):
    return [Path(p) for p in _os.listdir(self)]
methods['listdir'] = listdir
del listdir

def lstrip(self, chars=None):
    if chars is not None:
        chars = chars.replace(system_sep, SEP)
    return self.__class__((self._path + self._filename).lstrip(chars))
methods['lstrip'] = lstrip
del lstrip

def mkdir(self, mode=None):
    if mode is None:
        _os.mkdir(self)
    else:
        _os.mkdir(self, mode)
methods['mkdir'] = mkdir
del mkdir

def mkdirs(self, mode=None):
    path = self.vol
    elements = self.dir_elements
    for dir in elements:
        path /= dir
        if not path.exists():
            path.mkdir(mode)
methods['mkdirs'] = mkdirs
del mkdirs

def move(self, dst):
    'thin wrapper around shutil.move'
    if isinstance(dst, self.__class__):
        dst = self.base_cls(dst)
    src = self.base_cls(self)
    print src, dst
    _shutil.move(src, dst)
methods['move'] = move
del move

def rename(self, dst):
    'thin wrapper around os.rename)'
    if isinstance(dst, self.__class__):
        dst = self.base_cls(dst)
    src = self.base_cls(self)
    _os.rename(src, dst)
methods['rename'] = rename
del rename

def replace(self, old, new, count=None):
    old = old.replace(system_sep, SEP)
    new = new.replace(system_sep, SEP)
    if count:
        return self.__class__((self._path + self._filename).replace(old, new, count))
    else:
        return self.__class__((self._path + self._filename).replace(old, new))
methods['replace'] = replace
del replace

def rmdir(self):
    'thin wrapper around os.rmdir'
    _os.rmdir(self)
methods['rmdir'] = rmdir
del rmdir

def rmtree(self, ignore_errors=None, onerror=None):
    'thin wrapper around shutil.rmtree'
    target = self.base_cls(self)
    if ignore_errors is None and onerror is None:
        _shutil.rmtree(target)
    elif ignore_errors is not None and onerror is None:
        _shutil.rmtree(target, ignore_errors)
    elif onerror is not None:
        _shutil.rmtree(target, ignore_errors, onerror)
methods['rmtree'] = rmtree
del rmtree

def rstrip(self, chars=None):
    if chars is not None:
        chars = chars.replace(system_sep, SEP)
    return self.__class__((self._path + self._filename).rstrip(chars))
methods['rstrip'] = rstrip
del rstrip

def startswith(self, prefix, start=None, end=None):
    if isinstance(prefix, String):
        new_prefix = prefix.replace(system_sep, SEP)
    else:
        try:
            new_prefix = prefix.__class__([x.replace(system_sep, SEP) for x in prefix])
        except:
            raise TypeError("Can't convert %r to %s implicitly" % (prefix.__class__, self.__class__.__name__))
    start = start or 0
    end = end or len(self)
    return (self._path + self._filename).startswith(new_prefix, start, end)
methods['startswith'] = startswith
del startswith

def stat(self):
    return _os.stat(self)
methods['stat'] = stat
del stat

def strip(self, chars=None):
    if chars is not None:
        chars = chars.replace(system_sep, SEP)
    return self.__class__((self._path + self._filename).strip(chars))
methods['strip'] = strip
del strip

def strip_ext(self, remove=1):
    if not remove:
        return self.__class__(self._path + self._base)
    ext = '.'.join(self._ext.split('.')[:-remove])
    return self.__class__(self._path + self._base + ext)
methods['strip_ext'] = strip_ext 
del strip_ext

def unlink(self):
    "thin wrapper around os.unlink"
    _os.unlink(self)
methods['unlink'] = unlink
methods['remove'] = unlink
del unlink

if pyver < 2.6:
    def walk(self, topdown=True, onerror=None):
        p = self.__class__
        for dirpath, dirnames, filenames in _os.walk(self, topdown, onerror):
            dirpath = p(dirpath)
            dirnames = [p(dn) for dn in dirnames]
            filenames = [p(fn) for fn in filenames]
            yield dirpath, dirnames, filenames
else:
    def walk(self, topdown=True, onerror=None, followlinks=False):
        p = self.__class__
        for dirpath, dirnames, filenames in _os.walk(self, topdown, onerror, followlinks):
            dirpath = p(dirpath)
            dirnames = [p(dn) for dn in dirnames]
            filenames = [p(fn) for fn in filenames]
            yield dirpath, dirnames, filenames
methods['walk'] = walk
del walk

sPath = type('sPath', (Path, str), methods)
uPath = type('uPath', (Path, unicode), methods)

def glob(pattern):
    return [Path(p) for p in native_glob(pattern)]

def listdir(dir):
    return [Path(p) for p in _os.listdir(dir)]
