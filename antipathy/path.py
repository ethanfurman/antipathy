"""
file path manipulation

Copyright: 2011-2019 Ethan Furman
"""

from os import F_OK, R_OK, W_OK, X_OK
import glob as _glob
import os as _os
import shutil as _shutil
import sys as _sys

__all__ = ['Path', 'F_OK', 'R_OK', 'W_OK', 'X_OK', 'ospath']

_py_ver = _sys.version_info[:2]

if _py_ver < (3, 0):
    bytes = str
    unicode = unicode
else:
    bytes = bytes
    unicode = str
    long = int

native_glob = _glob.glob
native_listdir = _os.listdir

system_sep = _os.path.sep

_is_win = _os.path.__name__ == 'ntpath'

class Path(object):
    """\
    vol = [ c: | //node/sharepoint | '' ]
    dirs  = [ / | ./ ] + path/to/somewhere/
    filename  = filename.part1.ext
    base  = filename
    ext   = .part1.ext
    """

    def __new__(cls, *paths):
        paths = tuple([ospath(p) for p in paths])
        if not paths:
            paths = (unicode(), )
        elif len(paths) == 1 and isinstance(paths[0], cls):
            return paths[0]
        if isinstance(paths[0], unicode):
            str_cls = unicode
            new_cls = uPath
        else:
            str_cls = bytes
            new_cls = bPath
        if not all_equal(paths, test=lambda p: isinstance(p, str_cls)):
            raise TypeError('invalid path types: %r' % ([type(p) for p in paths], ))
        p = new_cls.__new__(new_cls, *paths)
        return p

    @staticmethod
    def getcwd():
        p = Path(_os.getcwd())
        return p / p.__class__._EMPTY

    @classmethod
    def getcwdb(cls):
        if _py_ver < (3, 0):
            return cls.getcwd()
        else:
            return cls(_os.getcwdb()) / bPath._EMPTY

    @classmethod
    def getcwdu(cls):
        if _py_ver < (3, 0):
            return cls(_os.getcwdu()) / uPath._EMPTY
        else:
            return cls.getcwd()

    @staticmethod
    def glob(pattern=None):
        if pattern is None:
            pattern = uPath._STAR
        return [Path(p) for p in native_glob(pattern)]

    @staticmethod
    def listdir(dir=None):
        if dir is None:
            dir = uPath._DOT
        return [Path(p) for p in _os.listdir(dir)]

    @staticmethod
    def abspath(name):
        "can result in invalid path if symlinks are present"
        return Path(_os.path.abspath(name))

    @staticmethod
    def absolute(name):
        'returns path from root without resolving .. dirs'
        return Path(name).absolute()

    @staticmethod
    def access(file_name, mode):
        return Path(file_name).access(mode)

    @staticmethod
    def ascend(name):
        return Path(name).ascend()

    @staticmethod
    def chdir(subdir):
        return Path(subdir).chdir()

    if _py_ver >= (2, 6) and not _is_win:
        @classmethod
        def chflags(cls, flags, files):
            if isinstance(files, cls.basecls):
                files = Path.glob(files)
            for file in files:
                Path(file).chflags(flags)

    @classmethod
    def chmod(cls, mode, files):
        "thin wrapper around os.chmod"
        if isinstance(files, cls.basecls):
            files = Path.glob(files)
        for file in files:
            Path(file).chmod(mode)

    @classmethod
    def chown(cls, uid, gid, files):
        "thin wrapper around os.chown"
        if isinstance(files, cls.basecls):
            files = Path.glob(files)
        for file in files:
            Path(file).chown(uid, gid)

    if not _is_win:
        @staticmethod
        def chroot(subdir):
            return Path(subdir).chroot()

    @staticmethod
    def commonprefix(*paths):
        if not paths:
            return Path(unicode())
        elif len(paths) == 1 and not isinstance(paths[0], list):
            return Path(paths[0])
        elif (
                len(paths) > 1 and isinstance(paths[0], list) or
                not all_equal(paths, test=lambda x: type(x))
                ):
            raise TypeError('invalid path types: %r' % ([type(p) for p in paths], ))
        else:
            paths = [Path(p).elements for p in paths]
            common = []
            for prefixes in zip(*paths):
                if all_equal(prefixes):
                    common.append(prefixes[0])
                else:
                    break
            return Path(*common)

    @classmethod
    def copy(cls, files, dst):
        """
        thin wrapper around shutil.copy2  (files is optional)
        """
        if isinstance(files, cls.basecls):
            files = Path.glob(files)
        for file in files:
            Path(file).copy(dst)

    @staticmethod
    def copytree(src, dst):
        Path(src).copytree(dst)

    @staticmethod
    def descend(name):
        return Path(name).descend()

    @staticmethod
    def exists(file_name):
        return Path(file_name).exists()

    @staticmethod
    def expanduser(name='~'):
        return Path(_os.path.expanduser(name))

    @staticmethod
    def expandvars(name):
        return Path(_os.path.expandvars(name))

    @staticmethod
    def isabs(name):
        'thin wrapper os.path.isabs()'
        raise NotImplementedError()

    @staticmethod
    def isabsolute(name):
        'os.path.isabs + windows paths must have drive-letter'
        raise NotImplementedError()

    @staticmethod
    def isdir(name):
        return _os.path.isdir(name)

    @staticmethod
    def isfile(name):
        return _os.path.isfile(name)

    @staticmethod
    def islink(name):
        return _os.path.islink(name)

    @staticmethod
    def ismount(name):
        return _os.path.ismount(name)

    @staticmethod
    def iter_all(name):
        return Path(name).iter_all()

    @staticmethod
    def iter_dirs(name):
        return Path(name).iter_dirs(name)

    if hasattr(_os, 'lchmod'):

        @classmethod
        def lchmod(cls, mode, files):
            if isinstance(files, cls.basecls):
                files = Path.glob(files)
            for file in files:
                Path(file).lchmod(mode)

    if hasattr(_os, 'lchflags'):

        @classmethod
        def lchflags(cls, files, flags):
            if isinstance(files, cls.basecls):
                files = Path.glob(files)
            for file in files:
                Path(file).lchflags(flags)

    if hasattr(_os, 'lchown'):

        @classmethod
        def lchown(cls, files, uid, gid):
            if isinstance(files, cls.basecls):
                files = Path.glob(files)
            for file in files:
                Path(file).lchown(uid, gid)

    if hasattr(_os.path, 'lexists'):

        @staticmethod
        def lexists(name):
            return Path(name).lexists()

    @staticmethod
    def link(source, link_name):
        return Path(source).link(link_name)

    if hasattr(_os, 'lstat'):

        @staticmethod
        def lstat(name):
            return Path(name).lstat()

    if hasattr(_os, 'mkfifo'):

        @staticmethod
        def mkfifo(name, mode=None):
            return Path(name).mkfifo(mode)

    @staticmethod
    def mkdir(subdir, mode=None, owner=None):
        return Path(subdir).mkdir(mode=mode, owner=owner)

    @staticmethod
    def makedirs(subdir, mode=None, owner=None):
        return Path(subdir).makedirs(mode=mode, owner=owner)

    @classmethod
    def move(cls, sources, dst):
        dst = Path(dst)
        if isinstance(sources, cls.basecls):
            sources = Path.glob(sources)
        for source in sources:
            Path(source).move(dst)
        return dst

    @staticmethod
    def normcase(path):
        return Path(_os.path.normcase(path))

    @staticmethod
    def open(name, mode='r', buffering=None, encoding=None):
        "encoding is only supported on Python3+"
        return Path(name).open(mode, buffering, encoding)

    if not _is_win:

        @staticmethod
        def pathconf(name, config):
            return Path(name).pathconf(config)

        pathconf_names = _os.pathconf_names

        readlink = _os.readlink

    @staticmethod
    def realcase(path):
        "noop on posix, actual case of path on nt"
        raise NotImplementedError()

    @staticmethod
    def realpath(path):
        "return canonical path (all symlinks resolved)"
        return Path(_os.path.realpath(path))

    @classmethod
    def removedirs(cls, subdirs):
        if isinstance(subdirs, cls.basecls):
            subdirs = Path.glob(subdirs)
        for subdir in subdirs:
            Path(subdir).removedirs()

    @staticmethod
    def rename(old, new):
        return Path(old).rename(new)

    @staticmethod
    def renames(old, new):
        return Path(old).renames(new)

    @classmethod
    def rmdir(cls, subdirs):
        if isinstance(subdirs, cls.basecls):
            subdirs = Path.glob(subdirs)
        for subdir in subdirs:
            Path(subdir).rmdir()

    @classmethod
    def rmtree(cls, subdirs, ignore_errors=None, onerror=None):
        if isinstance(subdirs, cls.basecls):
            subdirs = Path.glob(subdirs)
        for subdir in subdirs:
            Path(subdir).rmtree(ignore_errors=ignore_errors, onerror=onerror)

    @staticmethod
    def samefile(path1, path2):
        return _os.path.samefile(path1, path2)

    @staticmethod
    def stat(name):
        return Path(name).stat()

    if not _is_win:

        @staticmethod
        def statvfs(name):
            return Path(name).statvfs()

    @staticmethod
    def symlink(source, link_name):
        return Path(source).symlink(link_name)

    @classmethod
    def unlink(cls, names):
        if isinstance(names, cls.basecls):
            names = Path.glob(names)
        for name in names:
            Path(name).unlink()

    @classmethod
    def utime(cls, names, times):
        if isinstance(names, cls.basecls):
            names = Path.glob(names)
        for name in names:
            Path(name).utime(times)

    if _py_ver >= (2, 6):

        @staticmethod
        def walk(subdir, topdown=True, onerror=None, followlinks=False):
            p = Path(subdir).__class__
            for dirpath, dirnames, filenames in _os.walk(subdir, topdown, onerror, followlinks):
                dirpath = p(dirpath)
                dirnames[:] = [p(dn) for dn in dirnames]
                filenames[:] = [p(fn) for fn in filenames]
                yield dirpath, dirnames, filenames
    else:
        @staticmethod
        def walk(subdir, topdown=True, onerror=None):
            p = Path(subdir).__class__
            for dirpath, dirnames, filenames in _os.walk(subdir, topdown, onerror):
                dirpath = p(dirpath)
                dirnames[:] = [p(dn) for dn in dirnames]
                filenames[:] = [p(fn) for fn in filenames]
                yield dirpath, dirnames, filenames
Path.basecls = bytes, str, unicode

class Methods(object):

    def __new__(cls, *paths):
        base_cls = cls.basecls[1]       # bytes or unicode
        if not paths:
            paths = (base_cls(), )
        elif len(paths) > 1:
            new_paths = []
            for first, second in zip(paths[:-1], paths[1:]):
                if second.startswith(('/', cls._SYS_SEP)):
                    new_paths[:] = []
                    continue
                new_paths.append(first.rstrip('/'))
            new_paths.append(second)
            paths = tuple(new_paths)
        slash = cls._SLASH
        string = slash.join(paths)
        vol = dirs = filename = base = ext = protocol = host = site = params = fragments = base_cls()
        if cls._SYS_SEP != '/':
            string = string.replace(cls._SYS_SEP, slash)
        pieces = string.split(slash)
        if string[:2] == slash+slash and string[2:3] != slash:           # usually '//'
            if len(pieces) < 4:
                raise ValueError('bad path: %r' % string)
            vol = slash.join(pieces[:4])
            pieces = pieces[4:]
            if pieces:
                pieces.insert(0, cls._EMPTY)
        elif string[1:2] == cls._COLON and _os.path.__name__ == 'ntpath':
            vol = pieces.pop(0)
        else:
            vol = cls._EMPTY
        if len(pieces) > 2 and pieces[0].endswith(cls._COLON) and not pieces[1]:
            protocol = pieces[0] + cls._SLASH + cls._SLASH
            if len(pieces) > 3:
                host = pieces[2]
            site = protocol + host
            pieces = pieces[2:]
            if cls._QUESTION in string:
                params = string.split(cls._QUESTION)[1].split(cls._HASHTAG)[0]
                params = params.split(cls._AMPERSAND)
                params = dict([p.split(cls._EQUALS) for p in params])
            if cls._HASHTAG in string:
                fragments = tuple(string.split(cls._HASHTAG)[1].split(cls._AMPERSAND))
        if len(pieces) > 2:
            pieces = pieces[:1] + [p for p in pieces[1:-1] if p] + pieces[-1:]
        if pieces:
            if pieces[-1] in (cls._CUR_DIR, cls._PREV_DIR, cls._EMPTY):
                dirs = slash.join(pieces)
            else:
                dirs = slash.join(pieces[:-1])
                if pieces[:-1]:
                    dirs += slash
                filename = pieces[-1]
                ext_start = filename.rfind(cls._DOT)
                if ext_start != -1:
                    base, ext = filename[:ext_start], filename[ext_start:]
                else:
                    base = filename
        p = base_cls.__new__(cls, protocol + vol + dirs + filename)
        p._vol = vol
        p._dirs = dirs
        p._dirname = vol + dirs
        p._filename = filename
        p._base = base
        p._ext = ext
        p._protocol = protocol
        p._host = host
        p._site = site
        p._parameters = params
        p._fragments = fragments
        return p

    @property
    def protocol(self):
        return self._protocol[:-3]

    @property
    def host(self):
        return self._host

    @property
    def site(self):
        return self._site

    @property
    def parameters(self):
        return self._parameters

    @property
    def fragments(self):
        return self._fragments

    @property
    def vol(self):
        'volume/drive of path'
        return self.__class__(self._vol)
    drive = vol

    @property
    def root(self):
        if self._dirs[:1] == self._SLASH or self._vol[:1] == self._SLASH:
            return self.__class__(self._SLASH)
        else:
            return self._EMPTY

    @property
    def anchor(self):
        'pathlib: drive+root'
        return self.drive + self.root

    @property
    def dirs(self):
        'directories without volume/drive'
        result = self.__class__(self._dirs)
        if len(result) > 1:
            result = result.rstrip(self._SLASH)
        return result

    @property
    def parent(self):
        'first half of os.path.split(...)'
        return self.__class__(self._vol + self._dirs)
    dirname = parent

    @property
    def path(self):
        'self - for compatibility with stdlib'
        return self

    @property
    def filename(self):
        'second half of os.path.split(...)'
        return self.__class__(self._filename)
    name = basename = filename

    @property
    def base(self):
        return self.__class__(self._base)
    stem = base

    @property
    def ext(self):
        return self.__class__(self._ext)
    suffix = ext

    @property
    def suffixes(self):
        return [self.__class__(e) for e in self._filename.split('.')[1:]]

    @property
    def elements(self):
        return list(self.iter_all())
    parts = elements

    @property
    def dir_elements(self):
        return list(self.iter_dirs())

    def __add__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        return Path(self._dirname + self._filename + other)

    def __contains__(self, text):
        text = text.replace(self._SYS_SEP, self._SLASH)
        return text in self._dirname+self._filename

    def __div__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = Path(other)
        current = self.__class__()
        if other._vol or other._protocol:
            if self:
                raise ValueError("Cannot combine %r and %r" % (self, other))
            # current = other._vol
        current += self._protocol + self._dirname + self._filename
        if current[-1:] == self._SLASH:
            current = current[:-1]
        next = other._dirs + other._filename
        if next[:1] == self._SLASH:
            next = next[1:]
        return Path(current + self._SLASH + next)
    __truediv__ = __div__

    def __eq__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = Path(other)
        return self._protocol == other._protocol and self._dirname == other._dirname and self._filename == other._filename

    def __hash__(self):
        return (self._protocol + self._dirname + self._filename).__hash__()

    def __mod__(self, other):
        return Path((self._protocol + self._dirname + self._filename) % other)

    def __mul__(self, other):
        """
        if other.vol, self is ignored;
        if other.protocol, other.protocol is ignored
        """
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = Path(other)
        if other._vol:
            vol = other._vol
            current = []
        else:
            protocol = self._protocol
            vol = self._vol
            current = self.dir_elements
            if self._filename:
                current.append(self._filename)
        next = other.dir_elements
        if next and next[0] == self._SLASH:
            current = []
        dirs = current + next
        filename = other._filename
        new_path = []
        for dir in dirs:
            if dir not in (self._CUR_DIR, self._PREV_DIR):
                new_path.append(dir)
            elif dir == self._PREV_DIR:
                if len(new_path) == 1 and new_path[0] in (self._SLASH):
                    raise ValueError("Too many .. dirs in %s" % dirs)
                elif not new_path or new_path[-1] == self._PREV_DIR:
                    new_path.append(dir)
                else:
                    new_path.pop()
        if len(new_path) > 1 and new_path[0] == self._SLASH:
            new_path[0] = self._EMPTY
        dirs = self._SLASH.join(new_path)
        if dirs[-1:] != self._SLASH:
            dirs += self._SLASH
        if (vol[:2] == self._SLASH*2 or protocol) and dirs[:1] != self._SLASH:
            dirs = self._SLASH + dirs
        return Path(self._EMPTY.join([vol or protocol, dirs, filename]))

    def __ne__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        return not self == other

    def __radd__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        return Path(other + self._protocol + self._dirname + self._filename)

    def __rdiv__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = Path(other)
        return other / self
    __rtruediv__ = __rdiv__

    def __repr__(self):
        string = ''
        if self._protocol:
            string = self._protocol
        string += self._dirname + self._filename
        return "Path(%r)" % string

    def __rmod__(self, other):
        return other % (self._protocol + self._dirname + self._filename)

    def __rmul__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = Path(other)
        return other * self

    def __rsub__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = Path(other)
        return other - self

    def __str__(self):
        string = ''
        if self._protocol:
            string = self._protocol
        string += self._dirname + self._filename
        return string

    def __sub__(self, other):
        if not isinstance(other, self.basecls):
            return NotImplemented
        other = Path(other)
        if other == self._EMPTY:
            return self
        if other._vol != self._vol or other._protocol != self._protocol:
            raise ValueError("cannot subtract %r from %r" % (other, self))
        vol = self._EMPTY
        o = other._dirs + other._filename
        s = self._dirs + self._filename
        if not s.startswith(o):
            raise ValueError("cannot subtract %r from %r" % (other, self))
        return Path(vol+s[len(o):])

    def access(self, file_name, mode=None):
        if mode is None:
            mode = file_name
            file_name = self
        else:
            file_name = self/file_name
        file_name = base_class(file_name)
        return _os.access(file_name, mode)

    def ascend(self):
        pieces = self.elements
        absolute = self[0:1] == self._SYS_SEP
        lead = None
        if absolute:
            lead, pieces[0] = pieces[0], ''
        while len(pieces) > 1:
            yield self.__class__(self._SYS_SEP.join(pieces))
            pieces.pop()
        if absolute:
            yield lead

    def chdir(self, subdir=None):
        if subdir is None:
            subdir = self
        else:
            subdir = self/subdir
        subdir = base_class(subdir)
        _os.chdir(subdir)
        return subdir

    if (2, 6) <= _py_ver < (3, 3) and not _is_win:

        def chflags(self, flags, files=None):
            if files is None:
                files = [self]
            elif isinstance(files, self.basecls):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                file = base_class(file)
                _os.chflags(file, flags)

    elif _py_ver >= (3, 3) and not _is_win:

        def chflags(self, flags, files=None, follow_symlinks=True):
            if files is None:
                files = [self]
            elif isinstance(files, self.basecls):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                file = base_class(file)
                if follow_symlinks == True:
                    _os.chflags(file, flags)
                elif follow_symlinks == False:
                    _os.chflags(file, flags, follow_symlinks=False)
                else:
                    raise ValueError('follow_symlinks must be True or False, not %r' % follow_symlinks)

    if _py_ver < (3, 3):

        def chmod(self, mode, files=None):
            "thin wrapper around os.chmod"
            if files is None:
                files = [self]
            elif isinstance(files, self.basecls):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                file = base_class(file)
                _os.chmod(file, mode)

    else:

        def chmod(self, mode, files=None, follow_symlinks=True):
            "thin wrapper around os.chmod"
            if files is None:
                files = [self]
            elif isinstance(files, self.basecls):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                file = base_class(file)
                if follow_symlinks == True:
                    _os.chmod(file, mode)
                elif follow_symlinks == False:
                    _os.chmod(file, mode, follow_symlinks=False)
                else:
                    raise ValueError('follow_symlinks must be True or False, not %r' % follow_symlinks)

    if _py_ver < (3, 3):

        def chown(self, uid, gid, files=None):
            "thin wrapper around os.chown"
            if files is None:
                files = [self]
            elif isinstance(files, self.basecls):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                file = base_class(file)
                _os.chown(file, uid, gid)

    else:

        def chown(self, uid, gid, files=None, follow_symlinks=True):
            "thin wrapper around os.chown"
            if files is None:
                files = [self]
            elif isinstance(files, self.basecls):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                file = base_class(file)
                if follow_symlinks == True:
                    _os.chown(file, uid, gid)
                elif follow_symlinks == False:
                    _os.chown(file, uid, gid, follow_symlinks=False)
                else:
                    raise ValueError('follow_symlinks must be True or False, not %r' % follow_symlinks)

    if not _is_win:
        def chroot(self, subdir=None):
            if subdir is None:
                subdir = self
            else:
                subdir = self/subdir
            _os.chroot(self/subdir)
            return subdir

    def copy(self, files, dst=None):
        """
        thin wrapper around shutil.copy2  (files is optional)
        """
        if dst is None:
            dst, files = files, None
        if files is None:
            files = [self]
        elif isinstance(files, self.basecls):
            files = self.glob(files)
        else:
            files = [f for fs in files for f in self.glob(fs)]
        dst = base_class(dst)
        for file in files:
            src = base_class(file)
            _shutil.copy2(src, dst)

    if _py_ver < (2, 6):

        def copytree(self, dst, symlinks=False):
            'thin wrapper around shutil.copytree'
            src, dst = base_class(self, dst)
            _shutil.copytree(src, dst, symlinks)

    else:

        def copytree(self, dst, symlinks=False, ignore=None):
            'thin wrapper around shutil.copytree'
            src, dst = base_class(self, dst)
            _shutil.copytree(src, dst, symlinks, ignore)

    def count(self, sub, start=None, end=None):
        new_sub = sub.replace(self._SYS_SEP, self._SLASH)
        start = start or 0
        end = end or len(self)
        return (self._protocol + self._dirname + self._filename).count(new_sub)

    def descend(self):
        pieces = self.elements
        if not pieces:
            return
        lead, pieces = pieces[0], pieces[1:]
        yield lead
        for p in pieces:
            lead /= p
            yield lead

    def endswith(self, suffix, start=None, end=None):
        if isinstance(suffix, self.basecls):
            new_suffix = suffix.replace(self._SYS_SEP, self._SLASH)
        else:
            try:
                new_suffix = suffix.__class__([x.replace(self._SYS_SEP, self._SLASH) for x in suffix])
            except:
                raise TypeError("Can't convert %r implicitly" % suffix.__class__)
        start = start or 0
        end = end or len(self)
        return (self._protocol + self._dirname + self._filename).endswith(new_suffix, start, end)

    def exists(self, name=None):
        if name is not None:
            self /= name
        self = base_class(self)
        return _os.path.exists(self)

    def find(self, sub, start=None, end=None):
        new_sub = sub.replace(self._SYS_SEP, self._SLASH)
        start = start or 0
        end = end or len(self)
        return (self._protocol + self._dirname + self._filename).find(new_sub)

    def format(self, other):
        raise AttributeError("'Path' object has no attribute 'format'")

    def format_map(self, other):
        raise AttributeError("'Path' object has no attribute 'format_map'")

    def glob(self, pattern=None):
        if self and pattern:
            pattern = self/pattern
        elif self and (self._STAR in self or self._QUESTION in self):
                pattern = self
        elif self:
                pattern = self / self._STAR
        elif pattern:
            pass
        else:
            pattern = self._STAR
        return [Path(p) for p in native_glob(pattern)]

    def index(self, sub, start=None, end=None):
        result = self.find(sub, start, end)
        if result == -1:
            raise ValueError('substring not found')
        return result

    def isdir(self, name=None):
        if name is not None:
            self /= name
        self = base_class(self)
        return _os.path.isdir(self)

    def isfile(self, name=None):
        if name is not None:
            self /= name
        self = base_class(self)
        return _os.path.isfile(self)

    def islink(self, name=None):
        if name is not None:
            self /= name
        self = base_class(self)
        return _os.path.islink(self)

    def ismount(self, name=None):
        if name is not None:
            self /= name
        self = base_class(self)
        return _os.path.ismount(self)

    def iter_all(self, name=None):
        if name is not None:
            self /= name
        result = list(self.iter_dirs())
        if self.vol:
            result.insert(0, self.vol)
        if self.filename:
            result.append(self.filename)
        return iter(result)

    def iter_dirs(self, name=None):
        if name is not None:
            self /= name
        result = []
        cls = self.__class__
        if self._dirs:
            if self._dirs[0] == self._SLASH:
                result = [cls(self._SLASH)]
            dirs = self._dirs.strip(self._SLASH)
            if dirs:
                result.extend([cls(d) for d in dirs.split(self._SLASH)])
        return iter(result)

    if hasattr(_os, 'lchflags'):

        def lchflags(self, flags, files=None):
            if files is None:
                files = [self]
            elif isinstance(files, self.basecls):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                file = base_class(file)
                _os.chflags(file, flags)

    if hasattr(_os, 'lchmod'):

        def lchmod(self, mode, files=None):
            if files is None:
                files = [self]
            elif isinstance(files, self.basecls):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                file = base_class(file)
                _os.lchmod(file, mode)

    if hasattr(_os, 'lchown'):

        def lchown(self, uid, gid, files=None):
            if files is None:
                files = [self]
            elif isinstance(files, self.basecls):
                files = self.glob(files)
            else:
                files = [f for fs in files for f in self.glob(fs)]
            for file in files:
                file = base_class(file)
                _os.lchown(file, uid, gid)

    if hasattr(_os.path, 'lexists'):

        def lexists(self, file_name=None):
            if file_name is not None:
                self /= file_name
            self = base_class(self)
            return _os.path.lexists(self)

    if not _is_win:
        def link(self, source, new_name=None):
            'source is optional'
            if new_name is None:
                new_name = source
                source = self
            else:
                source = self/source
            source, new_name = base_class(source, new_name)
            return _os.link(source, new_name)

    def listdir(self, subdir=None):
        if self and subdir:
            subdir = self / subdir
        elif self:
            subdir = self
        elif subdir:
            pass
        else:
            subdir = self.__class__(self._DOT)
        return [Path(p) for p in _os.listdir(subdir)]

    if hasattr(_os, 'lstat'):

        def lstat(self, file_name=None):
            if file_name is not None:
                self /= file_name
            self = base_class(self)
            return _os.lstat(self)

    def lstrip(self, chars=None):
        if chars is not None:
            chars = chars.replace(self._SYS_SEP, self._SLASH)
        return self.__class__((self._protocol + self._dirname + self._filename).lstrip(chars))

    if hasattr(_os, 'mkfifo'):

        def mkfifo(self, name, mode=None):
            if mode is None:
                mode = name
                name = self
            else:
                name = self/name
            name = base_class(name)
            return _os.mkfifo(name, mode)

    def mkdir(self, subdirs=None, mode=None, owner=None):
        """
        Create a directory, setting owner if given.
        """
        if subdirs is not None and not isinstance(subdirs, self.basecls):
            if mode and owner:
                raise ValueError('subdirs should be a string or Path instance, not %r' % type(subdirs))
            if not owner:
                owner, mode, subdirs = mode, subdirs, None
            else:
                mode, subdirs = subdirs, None
        if subdirs is None:
            subdirs = [self]
        elif isinstance(subdirs, self.basecls):
            subdirs = [self/subdirs]
        else:
            subdirs = [d for ds in subdirs for d in self.glob(ds)]
        if mode is None:
            for subdir in subdirs:
                subdir = base_class(subdir)
                _os.mkdir(subdir)
                if owner is not None:
                    _os.chown(subdir, *owner)
        else:
            for subdir in subdirs:
                subdir = base_class(subdir)
                _os.mkdir(subdir, mode)
                if owner is not None:
                    _os.chown(subdir, *owner)

    def makedirs(self, subdirs=None, mode=None, owner=None):
        """
        Create any missing intermediate directories, setting owner if given.
        """
        if subdirs is not None and not isinstance(subdirs, self.basecls):
            if mode and owner:
                raise ValueError('subdirs should be a string or Path instance, not %r' % type(subdirs))
            if not owner:
                owner, mode, subdirs = mode, subdirs, None
            else:
                mode, subdirs = subdirs, None
        if subdirs is None:
            subdirs = [self]
        elif isinstance(subdirs, self.basecls):
            subdirs = [self/subdirs]
        else:
            subdirs = [d for ds in subdirs for d in self.glob(ds)]
        for subdir in subdirs:
            # path = subdir.vol
            path = Path()
            elements = subdir.elements
            for dir in elements:
                path /= dir
                if not path.exists():
                    path.mkdir(mode=mode, owner=owner)

    def move(self, files, dst=None):
        """
        thin wrapper around shutil.move  (files is optional)
        """
        if dst is None:
            dst, files = files, None
        if files is None:
            files = [self]
        elif isinstance(files, self.basecls):
            files = self.glob(files)
        else:
            files = [f for fs in files for f in self.glob(fs)]
        dst = base_class(dst)
        for file in files:
            src = base_class(file)
            _shutil.move(src, dst)
        return dst

    def open(self, file_name=None, mode=None, buffering=None, encoding=None):
        """
        encoding is only supported on Python3+
        """
        if isinstance(mode, (int, long)):
            if buffering is not None:
                raise ValueError('buffering specified by name and position? [mode=%r, buffering=%r]' % (mode, buffering))
            buffering, mode = mode, None
        if (
                file_name is not None and
                not isinstance(file_name, Path) and
                file_name.strip('Ubt') in ('r','w','a', 'x','r+','w+','a+')
            ):
            if mode is None:
                mode, file_name = file_name, None
        if file_name is None:
            file_name = self
        else:
            file_name = self/file_name
        file_name = base_class(file_name)
        if mode is None:
            mode = 'r'
        if buffering is encoding is None:
            return open(file_name, mode)
        elif encoding is None:
            return open(file_name, mode, buffering)
        elif buffering is None:
            return open(file_name, mode, encoding=encoding)
        else:
            return open(file_name, mode, buffering, encoding)

    if not _is_win:

        def pathconf(self, name, conf_name=None):
            if conf_name is None:
                conf_name, name = name, None
            if name is not None:
                self /= name
            self = base_class(self)
            return _os.pathconf(self, conf_name)

        pathconf_names = _os.pathconf_names

        def readlink(self):
            self = base_class(self)
            return _os.readlink(self)

    def removedirs(self, subdirs=None):
        if subdirs is None:
            subdirs = [self]
        elif isinstance(subdirs, self.basecls):
            subdirs = self.glob(subdirs)
        else:
            subdirs = [d for ds in subdirs for d in self.glob(ds)]
        for subdir in subdirs:
            subdir = base_class(subdir)
            _os.removedirs(subdir)

    def rename(self, file_name, dst=None):
        'thin wrapper around os.rename)'
        if dst is None:
            dst = file_name
            file_name = self
        else:
            file_name = self/file_name
        src, dst = base_class(file_name, dst)
        _os.rename(src, dst)
        return dst

    def renames(self, file_name, dst=None):
        if dst is None:
            dst = file_name
            file_name = self
        else:
            file_name = self/file_name
        src, dst = base_class(file_name, dst)
        return _os.renames(src, dst)

    def replace(self, old, new, count=None):
        old = old.replace(self._SYS_SEP, self._SLASH)
        new = new.replace(self._SYS_SEP, self._SLASH)
        if count:
            return self.__class__((self._protocol + self._dirname + self._filename).replace(old, new, count))
        else:
            return self.__class__((self._protocol + self._dirname + self._filename).replace(old, new))

    def rmdir(self, subdirs=None):
        'thin wrapper around os.rmdir'
        if subdirs is None:
            subdirs = [self]
        elif isinstance(subdirs, self.basecls):
            subdirs = self.glob(subdirs)
        else:
            subdirs = [d for ds in subdirs for d in self.glob(ds)]
        for subdir in subdirs:
            subdir = base_class(subdir)
            _os.rmdir(subdir)

    def rmtree(self, subdirs=None, ignore_errors=None, onerror=None):
        'thin wrapper around shutil.rmtree'
        if subdirs is not None and not isinstance(subdirs, self.basecls):
            if ignore_errors and onerror:
                raise ValueError('subdirs should be a string or Path instance, not %r' % type(subdirs))
            if not onerror:
                onerror, ignore_errors, subdirs = ignore_errors, subdirs, None
            else:
                ignore_errors, subdirs = subdirs, None
        if subdirs is None:
            subdirs = [self]
        elif isinstance(subdirs, self.basecls):
            subdirs = self.glob(subdirs)
        else:
            subdirs = [d for ds in subdirs for d in self.glob(ds)]
        for target in subdirs:
            target = base_class(target)
            if ignore_errors is None and onerror is None:
                _shutil.rmtree(target)
            elif ignore_errors is not None and onerror is None:
                _shutil.rmtree(target, ignore_errors)
            elif onerror is not None:
                _shutil.rmtree(target, ignore_errors, onerror)

    def rstrip(self, chars=None):
        if chars is not None:
            chars = chars.replace(self._SYS_SEP, self._SLASH)
        return self.__class__((self._protocol + self._dirname + self._filename).rstrip(chars))

    def startswith(self, prefix, start=None, end=None):
        if isinstance(prefix, self.basecls):
            new_prefix = prefix.replace(self._SYS_SEP, self._SLASH)
        else:
            try:
                new_prefix = prefix.__class__([x.replace(self._SYS_SEP, self._SLASH) for x in prefix])
            except:
                raise TypeError("Can't convert %r to %s implicitly" % (prefix.__class__, self.__class__.__name__))
        start = start or 0
        end = end or len(self)
        return (self._protocol + self._dirname + self._filename).startswith(new_prefix, start, end)

    def stat(self, file_name=None):
        if file_name is not None:
            self /= file_name
        self = base_class(self)
        return _os.stat(self)

    if not _is_win:

        def statvfs(self, name=None):
            if name is not None:
                self /= name
            self = base_class(self)
            return _os.statvfs(self)

    def strip(self, chars=None):
        if chars is not None:
            chars = chars.replace(self._SYS_SEP, self._SLASH)
        return self.__class__((self._protocol + self._dirname + self._filename).strip(chars))

    def strip_ext(self, remove=1):
        remove_all = False
        if not remove or remove < 1:
            remove_all = True
            remove = -1
        while (remove_all or remove > 0) and self.ext:
            remove -= 1
            self = self.__class__(self._protocol + self._dirname + self._base)
        return self

    if not _is_win:
        def symlink(self, source, new_name=None):
            if new_name is None:
                new_name = source
                source = self
            else:
                source = self/source
            source, new_name = base_class(source, new_name)
            _os.symlink(source, new_name)
            return new_name

    def unlink(self, files=None):
        "thin wrapper around os.unlink"
        if files is None:
            files = [self]
        elif isinstance(files, self.basecls):
            files = self.glob(files)
        else:
            files = [f for fs in files for f in self.glob(fs)]
        for target in files:
            target = base_class(target)
            _os.unlink(target)
    remove = unlink

    def utime(self, files, times=None):
        """
        files is optional
        """
        if times is None:
            times = files
            files = [self]
        elif isinstance(files, self.basecls):
            files = self.glob(files)
        else:
            files = [f for fs in files for f in self.glob(fs)]
        for file in files:
            file = base_class(file)
            _os.utime(file, times)

    if _py_ver >= (2, 6):
        def walk(self, topdown=True, onerror=None, followlinks=False):
            if topdown not in (True, False):
                raise ValueError('topdown should be True or False, not %r' % topdown)
            p = self.__class__
            self = base_class(self)
            for dirpath, dirnames, filenames in _os.walk(self, topdown, onerror, followlinks):
                dirpath = p(dirpath)
                dirnames[:] = [p(dn) for dn in dirnames]
                filenames[:] = [p(fn) for fn in filenames]
                yield dirpath, dirnames, filenames
    else:
        def walk(self, topdown=True, onerror=None):
            if topdown not in (True, False):
                raise ValueError('topdown should be True or False, not %r' % topdown)
            p = self.__class__
            self = base_class(self)
            for dirpath, dirnames, filenames in _os.walk(self, topdown, onerror):
                dirpath = p(dirpath)
                dirnames[:] = [p(dn) for dn in dirnames]
                filenames[:] = [p(fn) for fn in filenames]
                yield dirpath, dirnames, filenames

class bPath(Methods, Path, bytes):
    _COLON = ':'.encode('ascii')
    _CUR_DIR = '.'.encode('ascii')
    _DOT = '.'.encode('ascii')
    _EMPTY = ''.encode('ascii')
    _PREV_DIR = '..'.encode('ascii')
    _SLASH = '/'.encode('ascii')
    _SYS_SEP = system_sep.encode('ascii')
    _QUESTION = '?'.encode('ascii')
    _HASHTAG = '#'.encode('ascii')
    _AMPERSAND = '&'.encode('ascii')
    _EQUALS = '='.encode('ascii')
    _STAR = '*'.encode('ascii')

class uPath(Methods, Path, unicode):
    _COLON = unicode(':')
    _CUR_DIR = unicode('.')
    _DOT = unicode('.')
    _EMPTY = unicode('')
    _PREV_DIR = unicode('..')
    _SLASH = unicode('/')
    _SYS_SEP = unicode(system_sep)
    _QUESTION = unicode('?')
    _HASHTAG = unicode('#')
    _AMPERSAND = unicode('&')
    _EQUALS = unicode('=')
    _STAR = unicode('*')

if _py_ver < (3, 0):
    bPath.basecls = bPath, bytes, uPath, unicode
    uPath.basecls = uPath, unicode, bPath, bytes
else:
    bPath.basecls = bPath, bytes
    uPath.basecls = uPath, unicode

if _py_ver < (3, 0):
    from xmlrpclib import Marshaller
    Marshaller.dispatch[bPath] = Marshaller.dump_string
else:
    from xmlrpc.client import Marshaller
    Marshaller.dispatch[bPath] = Marshaller.dump_bytes
Marshaller.dispatch[uPath] = Marshaller.dump_unicode
del Marshaller

def base_class(*paths):
    result = []
    for p in paths:
        if isinstance(p, uPath):
            p = unicode(p)
        elif isinstance(p, bPath):
            p = bytes(p)
        result.append(p)
    if len(paths) == 1:
        return result[0]
    else:
        return tuple(result)

def all_equal(iterator, test=None):
    '''if `test is None` do a straight equality test'''
    it = iter(iterator)
    if test is None:
        try:
            target = next(it)
            test = lambda x: x == target
        except StopIteration:
            return True
    for item in it:
        if not test(item):
            return False
    return True


def ospath(thing):
    try:
        return thing.__ospath__()
    except AttributeError:
        if isinstance(thing, (bytes, unicode)):
            return thing
        raise TypeError('%r must be a bytes, str, or path-like object, not %r' % (thing, type(thing)))

