version = 0, 82, 8, 1

from antipathy.path import *
import antipathy.path as _path
from antipathy import test

__all__ = _path.__all__

def set_py3_mode():
    _path.bPath.basecls = _path.bPath, bytes
    _path.uPath.basecls = _path.uPath, unicode
