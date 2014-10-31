"""\
Copyright
=========
    - Copyright: 2011-2014 Ethan Furman
    - Author: Ethan Furman
    - Contact: ethan@stoneleaf.us
    - Version: 0.80.00 as of 2014-10-30

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

from os import F_OK, R_OK, W_OK, X_OK
import glob as _glob
import os as _os
import shutil as _shutil
import sys as _sys

__all__ = ['Path', 'F_OK', 'R_OK', 'W_OK', 'X_OK']

_py_ver = _sys.version_info[:2]

if _py_ver < (3, 0):
    bytes = str
else:
    unicode = str

native_glob = _glob.glob
native_listdir = _os.listdir

system_sep = _os.path.sep

is_win = _os.path.__name__ == 'ntpath'

py_ver = _sys.version_info[:2]

version = 0, 77, 8

class Path(object):
    """\
    vol = [ c: | //node/sharepoint | '' ]
    dirs  = [ / | ./ ] + path/to/somewhere/
    filename  = filename.part1.ext
    base  = filename
    ext   = .part1.ext
    """

    @classmethod
    def getcwd(cls):
        p = cls(_os.getcwd())
        return p / p.__class__._EMPTY

    @classmethod
    def getcwdb(cls):
        if py_ver < (3, 0):
            return self.getcwd()
        else:
            return cls(_os.getcwdb()) / bPath._EMPTY

    @classmethod
    def getcwdu(cls):
        if py_ver < (3, 0):
            return cls(_os.getcwdu()) / uPath._EMPTY
        else:
            return self.getcwd()

    @staticmethod
    def glob(pattern):
        return [Path(p) for p in native_glob(pattern)]

    @staticmethod
    def listdir(dir):
        return [Path(p) for p in _os.listdir(dir)]

    @property
    def vol(self):
        return self.__class__(self._vol)

    @property
    def dirs(self):
        return self.__class__(self._dirs)

    @property
    def path(self):
        return self.__class__(self._path)

    @property
    def filename(self):
        return self.__class__(self._filename)

    @property
    def base(self):
        return self.__class__(self._base)

    @property
    def ext(self):
        return self.__class__(self._ext)

    @property
    def elements(self):
        return list(self.iter_all())

    @property
    def dir_elements(self):
        return list(self.iter_dirs())

    def iter_all(self):
        result = list(self.iter_dirs())
        if self.vol:
            result.insert(0, self.vol)
        if self.filename:
            result.append(self.filename)
        return iter(result)

    def iter_dirs(self):
        result = []
        cls = self.__class__
        if self._dirs:
            if self._dirs[0] == self._SLASH:
                result = [cls(self._SLASH)]
            dirs = self._dirs.strip(self._SLASH)
            if dirs:
                result.extend([cls(d) for d in dirs.split(self._SLASH)])
        return iter(result)

    def __new__(cls, string=''):
        if isinstance(string, cls):
            return string
        if isinstance(string, unicode):
            new_cls = uPath
            base_cls = unicode
        else:
            new_cls = bPath
            base_cls = bytes
        slash = new_cls._SLASH
        vol = dirs = filename = base = ext = base_cls()
        if system_sep != '/':
            string = string.replace(system_sep, slash)
        if string[:2] == slash+slash:           # usually '//'
            pieces = string.split(slash)
            vol = slash.join(pieces[:4])
            pieces = pieces[4:]
            if pieces:
                pieces.insert(0, new_cls._EMPTY)
        elif string[1:2] == new_cls._COLON and _os.path.__name__ == 'ntpath':
            vol, string = string[:2], string[2:]
            pieces = string.split(slash)
        else:
            vol = new_cls._EMPTY
            pieces = string.split(slash)
        for bit in pieces[1:-1]:
            if not bit:
                raise ValueError("bad path: %r" % string)
        if pieces:
            if pieces[-1] in (new_cls._CUR_DIR, new_cls._PREV_DIR, new_cls._EMPTY):
                dirs = slash.join(pieces)
            else:
                dirs = slash.join(pieces[:-1])
                if pieces[:-1]:
                    dirs += slash
                filename = pieces[-1]
                ext_start = filename.rfind(new_cls._DOT)
                if ext_start != -1:
                    base, ext = filename[:ext_start], filename[ext_start:]
                else:
                    base = filename
        p = base_cls.__new__(new_cls, vol + dirs + filename)
        p._vol = vol
        p._dirs = dirs
        p._path = vol + dirs
        p._filename = filename
        p._base = base
        p._ext = ext
        return p

    def __add__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        return self.__class__(self._path + self._filename + other)

    def __contains__(self, text):
        text = text.replace(system_sep, self._SLASH)
        return text in self._path+self._filename

    def __div__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = self.__class__(other)
        if other._vol:
            raise ValueError("Cannot combine %r and %r" % (self, other))
        current = self._path + self._filename
        if current[-1:] == self._SLASH:
            current = current[:-1]
        next = other._dirs + other._filename
        if next[:1] == self._SLASH:
            next = next[1:]
        return self.__class__(current + self._SLASH + next)
    __truediv__ = __div__

    def __eq__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = self.__class__(other)
        return self._path == other._path and self._filename == other._filename

    def __hash__(self):
        return (self._path + self._filename).__hash__()

    def __mod__(self, other):
        return self.__class__((self._path + self._filename) % other)

    def __mul__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = self.__class__(other)
        if other._vol:
            vol = other._vol
            current = []
        else:
            vol = self._vol
            current = self.dir_elements
        next = other.dir_elements
        if next and next[0] == self._SLASH:
            current = []
        dirs = current + next
        new_path = []
        for dir in dirs:
            if dir not in (self._CUR_DIR, self._PREV_DIR):
                new_path.append(dir)
            elif dir == self._PREV_DIR:
                if not new_path or new_path[-1] in (self._EMPTY, self._SLASH):
                    raise ValueError("Too many .. dirs in %s" % dirs)
                new_path.pop()
        if len(new_path) > 1 and new_path[0] == self._SLASH:
            new_path[0] = self._EMPTY
        dirs = self._SLASH.join(new_path)
        if dirs[-1:] != self._SLASH:
            dirs += self._SLASH
        base = self._base + other._base
        ext = self._ext + other._ext
        if vol[:2] == self._SLASH*2 and dirs[:1] != self._SLASH:
            dirs = self._SLASH + dirs
        return self.__class__(self._EMPTY.join([vol, dirs, base, ext]))

    def __ne__(self, other):
        return not self == other

    def __radd__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        return self.__class__(other + self._path + self._filename)

    def __rdiv__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = self.__class__(other)
        return other / self
    __rtruediv__ = __rdiv__

    def __repr__(self):
        string = self._path + self._filename
        return "Path(%r)" % string

    def __rmod__(self, other):
        return other % (self._path + self._filename)

    def __rmul__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = self.__class__(other)
        return other * self

    def __rsub__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = self.__class__(other)
        return other - self

    def __str__(self):
        string = self._path + self._filename
        return string

    def __sub__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = self.__class__(other)
        if other == self._EMPTY:
            return self
        if other._vol != self._vol:
            raise ValueError("cannot subtract %r from %r" % (other, self))
        vol = self._EMPTY
        o = other.dirs + other.filename
        s = self.dirs + self.filename
        if not s.startswith(o):
            raise ValueError("cannot subtract %r from %r" % (other, self))
        return self.__class__(vol+s[len(o):])

    def access(self, file_name, mode=None):
        if mode is None:
            mode = file_name
            file_name = self
        else:
            file_name = self/file_name
        return _os.access(file_name, mode)

    def chdir(self, subdir=None):
        if subdir is None:
            subdir = self
        else:
            subdir = self/subdir
        _os.chdir(subdir)
        return Path.getcwd()

    if py_ver >= (2, 6) and not is_win:
        def chflags(self, flags, files=None):
            if files is None:
                files = [self]
            elif isinstance(files, (self.basecls, Path)):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                _os.chflags(file, flags)

    def chmod(self, mode, files=None):
        "thin wrapper around os.chmod"
        if files is None:
            files = [self]
        elif isinstance(files, (self.basecls, Path)):
            files = self.glob(files)
        else:
            files = [f for fs in files for f in self.glob(fs)]
        for file in files:
            _os.chmod(file, mode)

    def chown(self, uid, gid, files=None):
        "thin wrapper around os.chown"
        if files is None:
            files = [self]
        elif isinstance(files, (self.basecls, Path)):
            files = self.glob(files)
        else:
            files = [f for fs in files for f in self.glob(fs)]
        for file in files:
            _os.chown(file, uid, gid)

    if not is_win:
        def chroot(self, subdir=None):
            if subdir is None:
                return _os.chroot(self)
            else:
                return _os.chroot(self/subdir)

    def copy(self, files, dst=None):
        """
        thin wrapper around shutil.copy2  (files is optional)
        """
        if dst is None:
            dst, files = files, None
        if files is None:
            files = [self]
        elif isinstance(files, (self.basecls, Path)):
            files = self.glob(files)
        else:
            files = [f for fs in files for f in self.glob(fs)]
        if isinstance(dst, self.__class__):
            dst = self.base_cls(dst)
        for file in files:
            src = self.base_cls(file)
            _shutil.copy2(src, dst)

    def copytree(self, dst, symlinks=False, ignore=None):
        'thin wrapper around shutil.copytree'
        if isinstance(dst, self.__class__):
            dst = self.base_cls(dst)
        src = self.base_cls(src)
        _shutil.copytree(src, dst, symlinks, ignore)

    def count(self, sub, start=None, end=None):
        new_sub = sub.replace(system_sep, self._SLASH)
        start = start or 0
        end = end or len(self)
        return (self._path + self._filename).count(new_sub)

    def endswith(self, suffix, start=None, end=None):
        if isinstance(suffix, self.basecls):
            new_suffix = suffix.replace(system_sep, self._SLASH)
        else:
            try:
                new_suffix = suffix.__class__([x.replace(system_sep, self._SLASH) for x in suffix])
            except:
                raise TypeError("Can't convert %r to str implicitly" % suffix.__class__)
        start = start or 0
        end = end or len(self)
        return (self._path + self._filename).endswith(new_suffix, start, end)

    def exists(self, file_name=None):
        if file_name is None:
            return _os.path.exists(self)
        else:
            return _os.path.exists(self/file_name)

    def find(sub, start=None, end=None):
        new_sub = sub.replace(system_sep, self._SLASH)
        start = start or 0
        end = end or len(self)
        return (self._path + self._filename).find(new_sub)

    def format(self, other):
        raise AttributeError("'Path' object has no attribute 'format'")

    def format_map(self, other):
        raise AttributeError("'Path' object has no attribute 'format_map'")

    def glob(self, pattern=None):
        if pattern is None:
            pattern = self
        else:
            pattern = self/pattern
        return [Path(p) for p in native_glob(pattern)]

    def index(self, sub, start=None, end=None):
        result = self.find(sub, start, end)
        if result == -1:
            raise ValueError('substring not found')

    def isdir(self, name=None):
        if name is None:
            return _os.path.isdir(self)
        else:
            return _os.path.isdir(self/name)

    def isfile(self, name=None):
        if name is None:
            return _os.path.isfile(self)
        else:
            return _os.path.isfile(self/name)

    def islink(self, name=None):
        if name is None:
            return _os.path.islink(self)
        else:
            return _os.path.islink(self/name)

    def ismount(self, name=None):
        if name is None:
            return _os.path.ismount(self)
        else:
            return _os.path.ismount(self/name)

    if py_ver >= (2, 6) and not is_win:
        def lchflags(self, flags, files=None):
            if files is None:
                files = [self]
            elif isinstance(files, (self.basecls, Path)):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                _os.chflags(file, flags)

    if not is_win:
        def lchmod(self, mode, files=None):
            if files is None:
                files = [self]
            elif isinstance(files, (self.basecls, Path)):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                _os.lchmod(file, mode)

        def lchown(self, uid, gid, files=None):
            if files is None:
                files = [self]
            elif isinstance(files, (self.basecls, Path)):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                _os.lchown(file, uid, gid)

    def lexists(self, file_name=None):
        if file_name is None:
            return _os.path.lexists(self)
        else:
            return _os.path.lexists(self/file_name)

    def link(self, source, new_name=None):
        'source is optional'
        if new_name is None:
            new_name = source
            source = self
        else:
            source = self/source
        return _os.link(source, new_name)

    if not is_win:
        def listdir(self, subdir=None):
            if subdir is None:
                return [Path(p) for p in _os.listdir(self)]
            else:
                return [Path(p) for p in _os.listdir(self/subdir)]

    def lstat(self, file_name=None):
        if file_name is None:
            return _os.lstat(self)
        else:
            return _os.lstat(self/file_name)

    def lstrip(self, chars=None):
        if chars is not None:
            chars = chars.replace(system_sep, self._SLASH)
        return self.__class__((self._path + self._filename).lstrip(chars))

    if not is_win:
        def mkfifo(self, name, mode=None):
            if mode is None:
                mode = name
                name = self
            else:
                name = self/name
            return _os.mkfifo(self, mode)

    def mkdir(self, subdirs=None, mode=None, owner=None):
        """
        Create a directory, setting owner if given.
        """
        if subdirs is not None and not isinstance(subdirs, (self.basecls, Path)):
            if mode and owner:
                raise ValueError('subdirs should be a string or Path instance, not %r' % type(subdirs))
            if not owner:
                owner, mode, subdirs = mode, subdirs, None
            else:
                mode, subdirs = subdirs, None
        if subdirs is None:
            subdirs = [self]
        elif isinstance(subdirs, (self.basecls, Path)):
            subdirs = [self/subdirs]
        else:
            subdirs = [d for ds in subdirs for d in self.glob(ds)]
        if mode is None:
            for subdir in subdirs:
                _os.mkdir(subdir)
        else:
            for subdir in subdirs:
                _os.mkdir(subdir, mode)
        if owner is not None:
            for subdir in subdirs:
                _os.chown(subdir, *owner)

    def mkdirs(self, subdirs=None, mode=None, owner=None):
        """
        Create any missing intermediate directories, setting owner if given.
        """
        if subdirs is not None and not isinstance(subdirs, (self.basecls, Path)):
            if mode and owner:
                raise ValueError('subdirs should be a string or Path instance, not %r' % type(subdirs))
            if not owner:
                owner, mode, subdirs = mode, subdirs, None
            else:
                mode, subdirs = subdirs, None
        if subdirs is None:
            subdirs = [self]
        elif isinstance(subdirs, (self.basecls, Path)):
            subdirs = self/subdirs
        else:
            subdirs = [d for ds in subdirs for d in self.glob(ds)]
        for subdir in subdirs:
            path = subdir.vol
            elements = subdir.elements
            for dir in elements:
                path /= dir
                if not path.exists():
                    path.mkdir(mode, owner)

    def move(self, files, dst=None):
        """
        thin wrapper around shutil.move  (files is optional)
        """
        if dst is None:
            dst, files = files, None
        if files is None:
            files = [self]
        elif isinstance(files, (self.basecls, Path)):
            files = self.glob(files)
        else:
            files = [f for fs in files for f in self.glob(fs)]
        if isinstance(dst, self.__class__):
            dst = self.base_cls(dst)
        for file in files:
            src = self.base_cls(file)
            _shutil.move(src, dst)

    def open(self, file_name=None, mode=None, buffering=None):
        if isinstance(mode, (int, long)):
            if buffering is not None:
                raise ValueError('buffering specified by name and position? [mode=%r, buffering=%r]' % (mode, buffering))
            buffering, mode = mode, None
        if file_name is not None and not isinstance(file_name, Path) and file_name.rstrip('r').rstrip('U') in ('r','w','a','r+','w+','a+'):
            if mode is None:
                mode, file_name = file_name, None
        if file_name is None:
            file_name = self
        else:
            file_name = self/file_name
        if mode is None:
            mode = 'r'
        if buffering is None:
            return open(file_name, mode)
        else:
            return open(file_name, mode, buffering)

    if not is_win:
        pathconf = _os.pathconf
        pathconf_names = staticmethod(_os.pathconf_names)

    if not is_win:
        readlink = _os.readlink

    def removedirs(self, subdirs=None):
        if subdirs is None:
            subdirs = [self]
        elif isinstance(subdirs, (self.basecls, Path)):
            subdirs = self.glob(subdirs)
        else:
            subdirs = [d for ds in subdirs for d in self.glob(ds)]
        for subdir in subdirs:
            _os.removedirs(subdir)

    def rename(self, file_name, dst=None):
        'thin wrapper around os.rename)'
        if dst is None:
            dst = file_name
            file_name = self
        else:
            file_name = self/file_name
        if isinstance(dst, self.__class__):
            dst = self.base_cls(dst)
        src = self.base_cls(file_name)
        _os.rename(src, dst)

    def renames(self, file_name, dst=None):
        if dst is None:
            dst = file_name
            file_name = self
        else:
            file_name = self/file_name
        return _os.renames(file_name, dst)

    def replace(self, old, new, count=None):
        old = old.replace(system_sep, self._SLASH)
        new = new.replace(system_sep, self._SLASH)
        if count:
            return self.__class__((self._path + self._filename).replace(old, new, count))
        else:
            return self.__class__((self._path + self._filename).replace(old, new))

    def rmdir(self, subdirs=None):
        'thin wrapper around os.rmdir'
        if subdirs is None:
            subdirs = [self]
        elif isinstance(subdirs, (self.basecls, Path)):
            subdirs = self.glob(subdirs)
        else:
            subdirs = [d for ds in subdirs for d in self.glob(ds)]
        for subdir in subdirs:
            _os.rmdir(subdir)

    def rmtree(self, subdirs=None, ignore_errors=None, onerror=None):
        'thin wrapper around shutil.rmtree'
        if subdirs is not None and not isinstance(subdirs, (self.basecls, Path)):
            if ignore_errors and onerror:
                raise ValueError('subdirs should be a string or Path instance, not %r' % type(subdirs))
            if not onerror:
                onerror, ignore_errors, subdirs = ignore_errors, subdirs, None
            else:
                ignore_errors, subdirs = subdirs, None
        if subdirs is None:
            subdirs = [self]
        elif isinstance(subdirs, (self.basecls, Path)):
            subdirs = self.glob(subdirs)
        else:
            subdirs = [d for ds in subdirs for d in self.glob(ds)]
        for target in subdirs:
            target = self.base_cls(target)
            if ignore_errors is None and onerror is None:
                _shutil.rmtree(target)
            elif ignore_errors is not None and onerror is None:
                _shutil.rmtree(target, ignore_errors)
            elif onerror is not None:
                _shutil.rmtree(target, ignore_errors, onerror)

    def rstrip(self, chars=None):
        if chars is not None:
            chars = chars.replace(system_sep, self._SLASH)
        return self.__class__((self._path + self._filename).rstrip(chars))

    def startswith(self, prefix, start=None, end=None):
        if isinstance(prefix, self.basecls):
            new_prefix = prefix.replace(system_sep, self._SLASH)
        else:
            try:
                new_prefix = prefix.__class__([x.replace(system_sep, self._SLASH) for x in prefix])
            except:
                raise TypeError("Can't convert %r to %s implicitly" % (prefix.__class__, self.__class__.__name__))
        start = start or 0
        end = end or len(self)
        return (self._path + self._filename).startswith(new_prefix, start, end)

    def stat(self, file_name=None):
        if file_name is None:
            return _os.stat(self)
        else:
            return _os.stat(self/file_name)

    if not is_win:
        statvfs = _os.statvfs

    def strip(self, chars=None):
        if chars is not None:
            chars = chars.replace(system_sep, self._SLASH)
        return self.__class__((self._path + self._filename).strip(chars))

    def strip_ext(self, remove=1):
        if not remove:
            return self.__class__(self._path + self._base)
        ext = self._CUR_DIR.join(self._ext.split(self._CUR_DIR)[:-remove])
        return self.__class__(self._path + self._base + ext)

    if not is_win:
        def symlink(self, source, new_name=None):
            if new_name is None:
                new_name = source
                source = self
            else:
                source = self/source
            return _os.symlink(source, new_name)

    def unlink(self, files=None):
        "thin wrapper around os.unlink"
        if files is None:
            files = [self]
        elif isinstance(files, (self.basecls, Path)):
            files = self.glob(files)
        else:
            files = [f for fs in files for f in self.glob(fs)]
        for target in files:
            _os.unlink(target)
    remove = unlink

    def utime(self, files, times=None):
        """
        files is optional
        """
        if times is None:
            times = files
            files = [self]
        elif isinstance(files, (self.basecls, Path)):
            files = self.glob(files)
        else:
            files = [f for fs in files for f in self.glob(fs)]
        for file in files:
            _os.utime(file, times)

    if py_ver >= (2, 6):
        def walk(self, topdown=True, onerror=None, followlinks=False):
            p = self.__class__
            for dirpath, dirnames, filenames in _os.walk(self, topdown, onerror, followlinks):
                dirpath = p(dirpath)
                dirnames = [p(dn) for dn in dirnames]
                filenames = [p(fn) for fn in filenames]
                yield dirpath, dirnames, filenames
    else:
        def walk(self, topdown=True, onerror=None):
            p = self.__class__
            for dirpath, dirnames, filenames in _os.walk(self, topdown, onerror):
                dirpath = p(dirpath)
                dirnames = [p(dn) for dn in dirnames]
                filenames = [p(fn) for fn in filenames]
                yield dirpath, dirnames, filenames

class bPath(Path, bytes):
    _COLON = ':'.encode('ascii')
    _CUR_DIR = '.'.encode('ascii')
    _DOT = '.'.encode('ascii')
    _EMPTY = ''.encode('ascii')
    _PREV_DIR = '..'.encode('ascii')
    _SLASH = '/'.encode('ascii')
bPath.basecls = bPath, bytes

class uPath(Path, unicode):
    _COLON = unicode(':')
    _CUR_DIR = unicode('.')
    _DOT = unicode('.')
    _EMPTY = unicode('')
    _PREV_DIR = unicode('..')
    _SLASH = unicode('/')
uPath.basecls = uPath, unicode
