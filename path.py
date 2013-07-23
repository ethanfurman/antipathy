"""\
Copyright
=========
    - Copyright: 2011 Ethan Furman
    - Author: Ethan Furman
    - Contact: ethan@stoneleaf.us
    - Version: 0.01.001 as of 14 Apr 2011

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

import sys
import os

native_listdir = os.listdir

class Path(str):
    """\
    vol = [ c: | //node/sharepoint | '' ]
    dirs  = [ / | ./ | // ] + path/to/somewhere/
    filename  = filename.part1.ext
    base  = filename.part1
    ext   = .ext
    """
    sep = os.path.sep
    curdir = '.' + sep
    case_sensitive = True
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
    def dir_pieces(self):
        result = []
        sep = self.sep
        if self._dirs[0] == sep:
            result = [sep]
        dirs = self._dirs.strip(sep)
        result.extend(dirs.split(sep))
        return result
    def __new__(cls, string='', sep=None):
        if isinstance(string, cls):
            return string
        vol = dirs = filename = base = ext = ''
        #- string = string.strip()
        sep = sep or '/'
        string = string.replace(cls.sep, sep).rstrip('.')
        pieces = string.split(sep)
        if (':' not in pieces[0] and ':' in string
            or ':' in pieces[0] and pieces[0][1:2] != ':'):
                raise ValueError("bad path: %r" % string)
        elif ':' in pieces[0]:
            vol = pieces.pop(0)
            if not vol[-1] == ':':
                vol, rel = vol.split(':')
                vol = vol + ':'
                pieces.insert(0, rel)
            else:
                pieces.insert(0, '')
        elif pieces[:2] == ['',''] and len(pieces) > 2:
            vol = cls.sep.join(pieces[:4])
            pieces = [''] + pieces[4:]
        for bit in pieces[1:-1]:
            if not bit:
                raise ValueError("bad path: %r" % string)
        if pieces:
            if pieces[-1] == '':    # path ended in /
                dirs = cls.sep.join(pieces)
            else:
                dirs = cls.sep.join(pieces[:-1])
                if pieces[:-1]:
                    dirs += cls.sep
                filename = pieces[-1]
                if filename[-1] == '.':
                    filename = filename[:-1]
                ext_start = filename.rfind('.')
                if ext_start != -1:
                    base, ext = filename[:ext_start], filename[ext_start:]
                else:
                    base = filename
        blank = str.__new__(cls)
        if cls.case_sensitive:
            upper = lambda x: x
        else:
            upper = lambda x: x.upper()
        p = str.__new__(cls, vol + dirs + filename)
        p._upper = upper
        p._vol = vol
        p._dirs = dirs
        p._path = vol + dirs
        p._filename = filename
        p._base = base
        p._ext = ext
        return p

    def __add__(self, other):
        if not isinstance(other, str):
            return NotImplemented
        return self.__class__(self._path + self._filename + other)

    def __contains__(self, text):
        text = text.replace('/', self.sep)
        return self._upper(text) in self._upper(self._path+self._filename)

    def __div__(self, other):
        if not isinstance(other, str):
            return NotImplemented
        other = self.__class__(other)
        if other._vol:
            raise ValueError("Cannot combine %r and %r" % (self, other))
        current = self._path + self._filename
        if current[-1:] == self.sep:
            current = current[:-1]
        next = other._dirs + other._filename
        if next[:1] == self.sep:
            next = next[1:]
        return self.__class__(current + self.sep + next)

    def __eq__(self, other):
        if not isinstance(other, str):
            return NotImplemented
        other = self.__class__(self._upper(other))
        return self._upper(self._path) == other._path and self._upper(self._filename) == other._filename

    def __hash__(self):
        return self._upper(self._path + self._filename).__hash__()

    def __mod__(self, other):
        return self.__class__((self._path + self._filename) % other)

    def __mul__(self, other):
        if not isinstance(other, str):
            return NotImplemented
        other = self.__class__(other)
        if other._vol:
            raise ValueError("Cannot combine %r and %r" % (self, other))
        vol = self._vol
        current = self._dirs
        next = other._dirs
        if current and next and next[0] == self.sep:
                dirs = current + next[1:]
        else:
            dirs = current + next
        new_path = []
        for dir in dirs.split(self.sep):
            if dir not in ('.','..'):
                new_path.append(dir)
            elif dir == '..':
                if not new_path or new_path[-1] == '':
                    raise ValueError("Too many .. dirs in %s" % dirs)
                new_path.pop()
        dirs = self.sep.join(new_path)
        base = self._base + other._base
        ext = self._ext + other._ext
        if vol[:2] == self.sep*2 and dirs[:1] != self.sep:
            dirs = self.sep + dirs
        return self.__class__(''.join([vol, dirs, base, ext]))

    def __ne__(self, other):
        return not self == other

    def __radd__(self, other):
        if not isinstance(other, str):
            return NotImplemented
        return self.__class__(other + self._path + self._filename)

    def __rdiv__(self, other):
        if not isinstance(other, str):
            return NotImplemented
        other = self.__class__(other)
        return other / self

    def __repr__(self):
        string = self._path + self._filename
        return "Path(%r)" % string

    def __rmod__(self, other):
        return other % (self._path + self._filename)

    def __rmul__(self, other):
        if not isinstance(other, str):
            return NotImplemented
        other = self.__class__(other)
        return other * self

    def __rsub__(self, other):
        if not isinstance(other, str):
            return NotImplemented
        other = self.__class__(other)
        return other - self

    __rtruediv__ = __rdiv__

    def __str__(self):
        string = self._path + self._filename
        return string

    def __sub__(self, other):
        if not isinstance(other, str):
            return NotImplemented
        other = self.__class__(other)
        o_vol, o_dirs, o_base, o_ext = other._vol, other._dirs, other._base, other._ext
        s_vol, s_dirs, s_base, s_ext = self._vol, self._dirs, self._base, self._ext
        upper = self._upper
        if o_vol:
            if upper(o_vol) != upper(s_vol):
                raise ValueError("cannot subtract %r from %r" % (o_vol, s_vol))
            vol = ''
        else:
            vol = s_vol
        if o_dirs:
            if not upper(s_dirs).startswith(upper(o_dirs)):
                raise ValueError("cannot subtract %r from %r" % (o_dirs, s_dirs))
            dirs = s_dirs[len(o_dirs):]
        else:
            dirs = s_dirs
        if o_base or o_ext:
            o_filename = o_base + o_ext
            if upper(dirs).startswith(upper(o_filename)):
                dirs = dirs[len(o_filename):]
                o_base = o_ext = ''
        if o_base:
            if upper(s_base).startswith(upper(o_base)):
                base = s_base[len(o_base):]
            else:
                raise ValueError("cannot subtract %r from %r" % (o_base, dirs + s_base))
        else:
            base = s_base
        if o_ext:
            if upper(s_ext).startswith(upper(o_ext)):
                ext = s_ext[len(o_ext):]
            else:
                raise ValueError("cannot subtract %r from %r" % (o_ext, dirs + s_ext))
        else:
            ext = s_ext
        if vol[:2] == self.sep*2 and not dirs[:1] == self.sep:
            dirs = self.sep + dirs
        return self.__class__(vol + dirs + base + ext)
    __truediv__ = __div__

    def count(self, sub, start=None, end=None):
        new_sub = self._upper(sub).replace('/', self.sep)
        start = start or 0
        end = end or len(self)
        return self._upper(self._path + self._filename).count(new_sub)

    def endswith(self, suffix, start=None, end=None):
        if isinstance(suffix, str):
            new_suffix = self._upper(suffix).replace('/', self.sep)
        else:
            try:
                new_suffix = suffix.__class__([self._upper(x).replace('/', self.sep) for x in suffix])
            except:
                raise TypeError("Can't convert %r to str implicitly" % suffix.__class__)
        start = start or 0
        end = end or len(self)
        return self._upper(self._path + self._filename).endswith(new_suffix, start, end)

    def find(sub, start=None, end=None):
        new_sub = self._upper(sub).replace('/', self.sep)
        start = start or 0
        end = end or len(self)
        return self._upper(self._path + self._filename).find(new_sub)

    def format(self, other):
        raise AttributeError("'Path' object has no attribute 'format'")

    def format_map(self, other):
        raise AttributeError("'Path' object has no attribute 'format_map'")

    def index(self, sub, start=None, end=None):
        result = self.find(sub, start, end)
        if result == -1:
            raise ValueError('substring not found')

    def lstrip(self, chars=None):
        if chars is not None:
            chars = chars.replace('/', self.sep)
            if not self.case_sensitive:
                chars = chars.lower() + chars.upper()
        return self.__class__((self._path + self._filename).lstrip(chars))

    def replace(self, old, new, count=None):
        if self.case_sensitive:
            if count:
                return self.__class__((self._path + self._filename).replace(old, new, count))
            else:
                return self.__class__((self._path + self._filename).replace(old, new))
        final = (self._path + self._filename)
        replacements = 0
        while True:
            ref = final.lower()
            old = old.lower()
            index = ref.find(old)
            if index == -1:
                break
            final = final[:index] + new + final[index+len(old):]
            replacements += 1
            if count is not None and replacements == count:
                break
        return self.__class__(final)
    def rstrip(self, chars=None):
        if chars is not None:
            chars = chars.replace('/', self.sep)
            if not self.case_sensitive:
                chars = chars.lower() + chars.upper()
        return self.__class__((self._path + self._filename).rstrip(chars))

    def startswith(self, prefix, start=None, end=None):
        if isinstance(prefix, str):
            new_prefix = self._upper(prefix).replace('/', self.sep)
        else:
            try:
                new_prefix = prefix.__class__([self._upper(x).replace('/', self.sep) for x in prefix])
            except:
                raise TypeError("Can't convert %r to str implicitly" % prefix.__class__)
        start = start or 0
        end = end or len(self)
        return self._upper(self._path + self._filename).startswith(new_prefix, start, end)

    def strip(self, chars=None):
        if chars is not None:
            chars = chars.replace('/', self.sep)
            if not self.case_sensitive:
                chars = chars.lower() + chars.upper()
        return self.__class__((self._path + self._filename).strip(chars))

    def strip_ext(self, remove=1):
        if not remove:
            return self.__class__(self._path + self._base)
        ext = '.'.join(self._ext.split('.')[:-remove])
        return self.__class__(self._path + self._base + ext)

def integrate():
    os.listdir = listdir
    sys.modules['__builtin__'].Path = Path

def listdir(path):
    return [Path(p) for p in native_listdir(path)]

