import os
import unittest
import antipathy
import shutil
import sys
import tempfile
from antipathy.path import Path, _is_win as is_win, _py_ver as py_ver, unicode, R_OK, X_OK, ospath


_skip = object()
def not_implemented(func):
    return _skip

class TestCase(unittest.TestCase):

    def __init__(self, *args, **kwds):
        empty_tests = []
        for name, attr in self.__dict__.items():
            if attr is _skip:
                empty_tests.append(name)
        for name in empty_tests:
            delattr(self, name)
        super(TestCase, self).__init__(*args, **kwds)


class TestPathBasics(TestCase):

    test_paths = (
        ("/temp/place/somefile.abc.xyz",
            '/temp/place/somefile.abc.xyz', '', '/temp/place', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("/temp/place/somefile.abc.",
            '/temp/place/somefile.abc.', '', '/temp/place', 'somefile.abc.', 'somefile.abc', '.'),
        ("/temp/place/somefile.abc",
            '/temp/place/somefile.abc', '', '/temp/place', 'somefile.abc', 'somefile', '.abc'),
        ("/temp/place/somefile.",
            '/temp/place/somefile.', '', '/temp/place', 'somefile.', 'somefile', '.'),
        ("/temp/place/somefile",
            '/temp/place/somefile', '', '/temp/place', 'somefile', 'somefile', ''),
        ("/temp/place/",
            '/temp/place/', '', '/temp/place', '', '', ''),
        ("/.xyz",
            '/.xyz', '', '/', '.xyz', '', '.xyz'),
        ("/temp/.xyz",
            '/temp/.xyz', '', '/temp', '.xyz', '', '.xyz'),
        (".xyz",
            '.xyz', '', '', '.xyz', '', '.xyz'),
        ("temp/place/somefile.abc.xyz",
            'temp/place/somefile.abc.xyz', '', 'temp/place', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("temp/place/somefile.abc.",
            'temp/place/somefile.abc.', '', 'temp/place', 'somefile.abc.', 'somefile.abc', '.'),
        ("temp/place/somefile.abc",
            'temp/place/somefile.abc', '', 'temp/place', 'somefile.abc', 'somefile', '.abc'),
        ("temp/place/somefile.",
            'temp/place/somefile.', '', 'temp/place', 'somefile.', 'somefile', '.'),
        ("temp/place/somefile",
            'temp/place/somefile', '', 'temp/place', 'somefile', 'somefile', ''),
        ("temp/place/",
            'temp/place/', '', 'temp/place', '', '', ''),
        (".xyz",
            '.xyz', '', '', '.xyz', '', '.xyz'),
        ("temp/.xyz",
            'temp/.xyz', '', 'temp', '.xyz', '', '.xyz'),
        ("//peer/share/temp/.xyz",
                '//peer/share/temp/.xyz', '//peer/share', '/temp', '.xyz', '', '.xyz'),
        ("/",
            '/', '', '/', '', '', ''),
        (".",
            '.', '', '.', '', '', ''),
        ("..",
            '..', '', '..', '', '', ''),
        )

    test_posix_paths = (
        ("c:\\temp\\place\\somefile.abc.xyz",
            'c:\\temp\\place\\somefile.abc.xyz', '', '', 'c:\\temp\\place\\somefile.abc.xyz', 'c:\\temp\\place\\somefile.abc', '.xyz'),
        ("c:\\temp\\place\\somefile.abc.",
            'c:\\temp\\place\\somefile.abc.', '', '', 'c:\\temp\\place\\somefile.abc.', 'c:\\temp\\place\\somefile.abc', '.'),
        ("c:\\temp\\place\\somefile.abc",
            'c:\\temp\\place\\somefile.abc', '', '', 'c:\\temp\\place\\somefile.abc', 'c:\\temp\\place\\somefile', '.abc'),
        ("c:\\temp\\place\\somefile.",
            'c:\\temp\\place\\somefile.', '', '', 'c:\\temp\\place\\somefile.', 'c:\\temp\\place\\somefile', '.'),
        ("c:\\temp\\place\\somefile",
            'c:\\temp\\place\\somefile', '', '', 'c:\\temp\\place\\somefile', 'c:\\temp\\place\\somefile', ''),
        ("c:\\temp\\place\\",
            'c:\\temp\\place\\', '', '', 'c:\\temp\\place\\', 'c:\\temp\\place\\', ''),
        ("c:\\.xyz",
            'c:\\.xyz', '', '', 'c:\\.xyz', 'c:\\', '.xyz'),
        ("c:\\temp\\.xyz",
            'c:\\temp\\.xyz', '', '', 'c:\\temp\\.xyz', 'c:\\temp\\', '.xyz'),
        ("c:temp\\place\\somefile.abc.xyz",
            'c:temp\\place\\somefile.abc.xyz', '', '', 'c:temp\\place\\somefile.abc.xyz', 'c:temp\\place\\somefile.abc', '.xyz'),
        ("c:temp\\place\\somefile.abc.",
            'c:temp\\place\\somefile.abc.', '', '', 'c:temp\\place\\somefile.abc.', 'c:temp\\place\\somefile.abc', '.'),
        ("c:temp\\place\\somefile.abc",
            'c:temp\\place\\somefile.abc', '', '', 'c:temp\\place\\somefile.abc', 'c:temp\\place\\somefile', '.abc'),
        ("c:temp\\place\\somefile.",
            'c:temp\\place\\somefile.', '', '', 'c:temp\\place\\somefile.', 'c:temp\\place\\somefile', '.'),
        ("c:temp\\place\\somefile",
            'c:temp\\place\\somefile', '', '', 'c:temp\\place\\somefile', 'c:temp\\place\\somefile', ''),
        ("c:temp\\place\\",
            'c:temp\\place\\', '', '', 'c:temp\\place\\', 'c:temp\\place\\', ''),
        ("c:.xyz",
            'c:.xyz', '', '', 'c:.xyz', 'c:', '.xyz'),
        ("c:temp\\.xyz",
            'c:temp\\.xyz', '', '', 'c:temp\\.xyz', 'c:temp\\', '.xyz'),
        ("\\temp\\place\\somefile.abc.xyz",
            '\\temp\\place\\somefile.abc.xyz', '', '', '\\temp\\place\\somefile.abc.xyz', '\\temp\\place\\somefile.abc', '.xyz'),
        ("\\temp\\place\\somefile.abc.",
            '\\temp\\place\\somefile.abc.', '', '', '\\temp\\place\\somefile.abc.', '\\temp\\place\\somefile.abc', '.'),
        ("\\temp\\place\\somefile.abc",
            '\\temp\\place\\somefile.abc', '', '', '\\temp\\place\\somefile.abc', '\\temp\\place\\somefile', '.abc'),
        ("\\temp\\place\\somefile.",
            '\\temp\\place\\somefile.', '', '', '\\temp\\place\\somefile.', '\\temp\\place\\somefile', '.'),
        ("\\temp\\place\\somefile",
            '\\temp\\place\\somefile', '', '', '\\temp\\place\\somefile', '\\temp\\place\\somefile', ''),
        ("\\temp\\place\\",
            '\\temp\\place\\', '', '', '\\temp\\place\\', '\\temp\\place\\', ''),
        ("\\.xyz",
            '\\.xyz', '', '', '\\.xyz', '\\', '.xyz'),
        ("\\temp\\.xyz",
            '\\temp\\.xyz', '', '', '\\temp\\.xyz', '\\temp\\', '.xyz'),
        ("temp\\place\\somefile.abc.xyz",
            'temp\\place\\somefile.abc.xyz', '', '', 'temp\\place\\somefile.abc.xyz', 'temp\\place\\somefile.abc', '.xyz'),
        ("temp\\place\\somefile.abc.",
            'temp\\place\\somefile.abc.', '', '', 'temp\\place\\somefile.abc.', 'temp\\place\\somefile.abc', '.'),
        ("temp\\place\\somefile.abc",
            'temp\\place\\somefile.abc', '', '', 'temp\\place\\somefile.abc', 'temp\\place\\somefile', '.abc'),
        ("temp\\place\\somefile.",
            'temp\\place\\somefile.', '', '', 'temp\\place\\somefile.', 'temp\\place\\somefile', '.'),
        ("temp\\place\\somefile",
            'temp\\place\\somefile', '', '', 'temp\\place\\somefile', 'temp\\place\\somefile', ''),
        ("temp\\place\\",
            'temp\\place\\', '', '', 'temp\\place\\', 'temp\\place\\', ''),
        ("temp\\.xyz",
            'temp\\.xyz', '', '', 'temp\\.xyz', 'temp\\', '.xyz'),

        ("c:/temp/place/somefile.abc.xyz",
            'c:/temp/place/somefile.abc.xyz', '', 'c:/temp/place', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("c:/temp/place/somefile.abc.",
            'c:/temp/place/somefile.abc.', '', 'c:/temp/place', 'somefile.abc.', 'somefile.abc', '.'),
        ("c:/temp/place/somefile.abc",
            'c:/temp/place/somefile.abc', '', 'c:/temp/place', 'somefile.abc', 'somefile', '.abc'),
        ("c:/temp/place/somefile.",
            'c:/temp/place/somefile.', '', 'c:/temp/place', 'somefile.', 'somefile', '.'),
        ("c:/temp/place/somefile",
            'c:/temp/place/somefile', '', 'c:/temp/place', 'somefile', 'somefile', ''),
        ("c:/temp/place/",
            'c:/temp/place/', '', 'c:/temp/place', '', '', ''),
        ("c:/.xyz",
            'c:/.xyz', '', 'c:', '.xyz', '', '.xyz'),
        ("c:/temp/.xyz",
            'c:/temp/.xyz', '', 'c:/temp', '.xyz', '', '.xyz'),
        ("c:temp/place/somefile.abc.xyz",
            'c:temp/place/somefile.abc.xyz', '', 'c:temp/place', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("c:temp/place/somefile.abc.",
            'c:temp/place/somefile.abc.', '', 'c:temp/place', 'somefile.abc.', 'somefile.abc', '.'),
        ("c:temp/place/somefile.abc",
            'c:temp/place/somefile.abc', '', 'c:temp/place', 'somefile.abc', 'somefile', '.abc'),
        ("c:temp/place/somefile.",
            'c:temp/place/somefile.', '', 'c:temp/place', 'somefile.', 'somefile', '.'),
        ("c:temp/place/somefile",
            'c:temp/place/somefile', '', 'c:temp/place', 'somefile', 'somefile', ''),
        ("c:temp/place/",
            'c:temp/place/', '', 'c:temp/place', '', '', ''),
        ("c:.xyz",
            'c:.xyz', '', '', 'c:.xyz', 'c:', '.xyz'),
        ("c:temp/.xyz",
            'c:temp/.xyz', '', 'c:temp', '.xyz', '', '.xyz'),
        )
    test_win_paths = (
        ("c:\\temp\\place\\somefile.abc.xyz",
            'c:/temp/place/somefile.abc.xyz', 'c:', '/temp/place', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("c:\\temp\\place\\somefile.abc.",
            'c:/temp/place/somefile.abc.', 'c:', '/temp/place', 'somefile.abc.', 'somefile.abc', '.'),
        ("c:\\temp\\place\\somefile.abc",
            'c:/temp/place/somefile.abc', 'c:', '/temp/place', 'somefile.abc', 'somefile', '.abc'),
        ("c:\\temp\\place\\somefile.",
            'c:/temp/place/somefile.', 'c:', '/temp/place', 'somefile.', 'somefile', '.'),
        ("c:\\temp\\place\\somefile",
            'c:/temp/place/somefile', 'c:', '/temp/place', 'somefile', 'somefile', ''),
        ("c:\\temp\\place\\",
            'c:/temp/place/', 'c:', '/temp/place', '', '', ''),
        ("c:\\.xyz",
            'c:/.xyz', 'c:', '/', '.xyz', '', '.xyz'),
        ("c:\\temp\\.xyz",
            'c:/temp/.xyz', 'c:', '/temp', '.xyz', '', '.xyz'),
        ("c:temp\\place\\somefile.abc.xyz",
            'c:temp/place/somefile.abc.xyz', 'c:', 'temp/place', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("c:temp\\place\\somefile.abc.",
            'c:temp/place/somefile.abc.', 'c:', 'temp/place', 'somefile.abc.', 'somefile.abc', '.'),
        ("c:temp\\place\\somefile.abc",
            'c:temp/place/somefile.abc', 'c:', 'temp/place', 'somefile.abc', 'somefile', '.abc'),
        ("c:temp\\place\\somefile.",
            'c:temp/place/somefile.', 'c:', 'temp/place', 'somefile.', 'somefile', '.'),
        ("c:temp\\place\\somefile",
            'c:temp/place/somefile', 'c:', 'temp/place', 'somefile', 'somefile', ''),
        ("c:temp\\place\\",
            'c:temp/place/', 'c:', 'temp/place', '', '', ''),
        ("c:.xyz",
            'c:.xyz', 'c:', '', '.xyz', '', '.xyz'),
        ("c:temp\\.xyz",
            'c:temp/.xyz', 'c:', 'temp', '.xyz', '', '.xyz'),
        ("\\temp\\place\\somefile.abc.xyz",
            '/temp/place/somefile.abc.xyz', '', '/temp/place', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("\\temp\\place\\somefile.abc.",
            '/temp/place/somefile.abc.', '', '/temp/place', 'somefile.abc.', 'somefile.abc', '.'),
        ("\\temp\\place\\somefile.abc",
            '/temp/place/somefile.abc', '', '/temp/place', 'somefile.abc', 'somefile', '.abc'),
        ("\\temp\\place\\somefile.",
            '/temp/place/somefile.', '', '/temp/place', 'somefile.', 'somefile', '.'),
        ("\\temp\\place\\somefile",
            '/temp/place/somefile', '', '/temp/place', 'somefile', 'somefile', ''),
        ("\\temp\\place\\",
            '/temp/place/', '', '/temp/place', '', '', ''),
        ("\\.xyz",
            '/.xyz', '', '/', '.xyz', '', '.xyz'),
        ("\\temp\\.xyz",
            '/temp/.xyz', '', '/temp', '.xyz', '', '.xyz'),
        ("temp\\place\\somefile.abc.xyz",
            'temp/place/somefile.abc.xyz', '', 'temp/place', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("temp\\place\\somefile.abc.",
            'temp/place/somefile.abc.', '', 'temp/place', 'somefile.abc.', 'somefile.abc', '.'),
        ("temp\\place\\somefile.abc",
            'temp/place/somefile.abc', '', 'temp/place', 'somefile.abc', 'somefile', '.abc'),
        ("temp\\place\\somefile.",
            'temp/place/somefile.', '', 'temp/place', 'somefile.', 'somefile', '.'),
        ("temp\\place\\somefile",
            'temp/place/somefile', '', 'temp/place', 'somefile', 'somefile', ''),
        ("temp\\place\\",
            'temp/place/', '', 'temp/place', '', '', ''),
        ("temp\\.xyz",
            'temp/.xyz', '', 'temp', '.xyz', '', '.xyz'),

        ("c:/temp/place/somefile.abc.xyz",
            'c:/temp/place/somefile.abc.xyz', 'c:', '/temp/place', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("c:/temp/place/somefile.abc.",
            'c:/temp/place/somefile.abc.', 'c:', '/temp/place', 'somefile.abc.', 'somefile.abc', '.'),
        ("c:/temp/place/somefile.abc",
            'c:/temp/place/somefile.abc', 'c:', '/temp/place', 'somefile.abc', 'somefile', '.abc'),
        ("c:/temp/place/somefile.",
            'c:/temp/place/somefile.', 'c:', '/temp/place', 'somefile.', 'somefile', '.'),
        ("c:/temp/place/somefile",
            'c:/temp/place/somefile', 'c:', '/temp/place', 'somefile', 'somefile', ''),
        ("c:/temp/place/",
            'c:/temp/place/', 'c:', '/temp/place', '', '', ''),
        ("c:/.xyz",
            'c:/.xyz', 'c:', '/', '.xyz', '', '.xyz'),
        ("c:/temp/.xyz",
            'c:/temp/.xyz', 'c:', '/temp', '.xyz', '', '.xyz'),
        ("c:temp/place/somefile.abc.xyz",
            'c:temp/place/somefile.abc.xyz', 'c:', 'temp/place', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("c:temp/place/somefile.abc.",
            'c:temp/place/somefile.abc.', 'c:', 'temp/place', 'somefile.abc.', 'somefile.abc', '.'),
        ("c:temp/place/somefile.abc",
            'c:temp/place/somefile.abc', 'c:', 'temp/place', 'somefile.abc', 'somefile', '.abc'),
        ("c:temp/place/somefile.",
            'c:temp/place/somefile.', 'c:', 'temp/place', 'somefile.', 'somefile', '.'),
        ("c:temp/place/somefile",
            'c:temp/place/somefile', 'c:', 'temp/place', 'somefile', 'somefile', ''),
        ("c:temp/place/",
            'c:temp/place/', 'c:', 'temp/place', '', '', ''),
        ("c:.xyz",
            'c:.xyz', 'c:', '', '.xyz', '', '.xyz'),
        ("c:temp/.xyz",
            'c:temp/.xyz', 'c:', 'temp', '.xyz', '', '.xyz'),
        )

    def test_errors(self):
        "check errors"
        self.assertRaises(ValueError, Path('/backups/').__div__, Path('//machine/share/temp/'))
        self.assertRaises(ValueError, Path('/backups/file1').__div__, Path('//machine/share/temp/'))
        self.assertRaises(ValueError, Path('/../backups/').__mul__, Path('temp/'))
        self.assertRaises(ValueError, Path('/backups/').__mul__, Path('../../temp/'))
        self.assertRaises(ValueError, Path('/backups').__mul__, Path('../../temp/'))
        self.assertRaises(ValueError, Path('/backups/').__mul__, Path('./../../temp/'))
        self.assertRaises(ValueError, Path('c:/backups').__sub__, Path('/backups/'))
        self.assertRaises(ValueError, Path('c:/backups/temp').__sub__, Path('backups/temp'))
        self.assertRaises(ValueError, Path('c:/backups.old/temp').__sub__, Path('temp.old'))
        self.assertRaises(ValueError, Path('c:/backups/temp').__sub__, Path('backups/temp'))
        self.assertRaises(ValueError, Path('//machine/share/backups/temp').__sub__, Path('backups/temp'))
        self.assertRaises(ValueError, Path('c:/backups/temp.old').__sub__, Path('c:/backups.old'))
        self.assertRaises(AttributeError, Path('/some/path').format, 'this')
        self.assertRaises(AttributeError, Path('/some/path').format_map, 'this')
        self.assertRaises(TypeError, Path('/some/other/path/').endswith, set(['an','ending','or','two']))
        self.assertRaises(TypeError, Path('/some/other/path/').startswith, set(['a','start','or','two']))

    def test_path(self):
        "check file paths"
        enum = 0
        for actual, expected, vol, dirs, filename, base, ext in self.test_paths:
            p = Path(actual)
            self.assertEqual(p, expected, "failed on iter %d --> %r != %r" % (enum, p, expected))
            self.assertEqual(p.vol, vol, "failed on iter %d --> %r != %r" % (enum, p.vol, vol))
            self.assertEqual(p.dirs, dirs, "failed on iter %d --> %r != %r" % (enum, p.dirs, dirs))
            self.assertEqual(p.filename, filename, "failed on iter %d --> %r != %r" % (enum, p.filename, filename))
            self.assertEqual(p.base, base, "failed on iter %d --> %r != %r" % (enum, p.base, base))
            self.assertEqual(p.ext,  ext, "failed on iter %d --> %r != %r" % (enum, p.ext, ext))
            enum += 1

    if os.path.__name__ == 'ntpath':
        def test_win_path(self):
            enum = 0
            for actual, expected, vol, dirs, filename, base, ext in self.test_win_paths:
                p = Path(actual)
                self.assertEqual(p, expected, "failed on iter %d --> %r != %r" % (enum, p, expected))
                self.assertEqual(p.vol, vol, "failed on iter %d --> %r != %r" % (enum, p.vol, vol))
                self.assertEqual(p.dirs, dirs, "failed on iter %d --> %r != %r" % (enum, p.dirs, dirs))
                self.assertEqual(p.filename, filename, "failed on iter %d --> %r != %r" % (enum, p.filename, filename))
                self.assertEqual(p.base, base, "failed on iter %d --> %r != %r" % (enum, p.base, base))
                self.assertEqual(p.ext,  ext, "failed on iter %d --> %r != %r" % (enum, p.ext, ext))
                enum += 1

    if os.path.__name__ == 'posixpath':
        def test_posix_path(self):
            enum = 0
            for actual, expected, vol, dirs, filename, base, ext in self.test_posix_paths:
                p = Path(actual)
                self.assertEqual(p, expected, "failed on iter %d --> %r != %r" % (enum, p, expected))
                self.assertEqual(p.vol, vol, "failed on iter %d --> %r != %r" % (enum, p.vol, vol))
                self.assertEqual(p.dirs, dirs, "failed on iter %d --> %r != %r" % (enum, p.dirs, dirs))
                self.assertEqual(p.filename, filename, "failed on iter %d --> %r != %r" % (enum, p.filename, filename))
                self.assertEqual(p.base, base, "failed on iter %d --> %r != %r" % (enum, p.base, base))
                self.assertEqual(p.ext,  ext, "failed on iter %d --> %r != %r" % (enum, p.ext, ext))
                enum += 1

    def test_os_path_join(self):
        "check os.path.join"
        if is_win:
            self.assertEqual(os.path.join(Path('c:'), Path('/temp/')), Path('c:/temp/'))
            self.assertEqual(os.path.join(Path('/temp/file'), Path('c:/root')), Path('c:/root'))
        else:
            self.assertEqual(os.path.join(Path('c:'), Path('/temp/')), Path('/temp/'))
            self.assertEqual(os.path.join(Path('/temp/file'), Path('c:/root')), Path('/temp/file/c:/root'))
        self.assertEqual(os.path.join(Path('c:/'), Path('temp/')), Path('c:/temp/'))

    def test_addition(self):
        "check path addition"
        self.assertEqual(Path('c:') + Path('/temp/'), Path('c:/temp/'))
        self.assertEqual(Path('c:/') + Path('temp/'), Path('c:/temp/'))
        self.assertEqual(Path('c:/temp/') + Path('backups/'), Path('c:/temp/backups/'))
        self.assertEqual(Path('/usr/local/bin') + Path(''), Path('/usr/local/bin'))

    def test_multiplication(self):
        "check path fusing"
        test_data = (
            ('', '/', '/'),
            ('/', '', '/'),
            ('/', 'temp/', '/temp/'),
            ('/', 'temp', '/temp'),
            ('/', '/temp/', '/temp/'),
            ('/', '/temp', '/temp'),
            ('/temp/', 'backups/', '/temp/backups/'),
            ('/temp/', 'backups', '/temp/backups'),
            ('/temp', 'backups', '/temp/backups'),
            ('/temp', 'backups/', '/temp/backups/'),
            ('/temp/', './backups/', '/temp/backups/'),
            ('/temp', './backups/', '/temp/backups/'),
            ('/temp/', './backups', '/temp/backups'),
            ('/temp', './backups', '/temp/backups'),
            ('/temp/', '/backups/', '/backups/'),
            ('/temp', '/backups/', '/backups/'),
            ('/temp/', '/backups', '/backups'),
            ('/temp', '/backups', '/backups'),
            ('/temp/this/./.tar', '../backup/./.gz', '/temp/this/backup/.gz'),
            ('/temp/this/./.tar/', '../backup/./.gz', '/temp/this/backup/.gz'),
            ('/temp/this/./', '../backup/./.gz', '/temp/backup/.gz'),
            ('/temp/this/.', '../backup/./.gz', '/temp/backup/.gz'),
            ('/temp/../', './backups/', '/backups/'),
            ('/temp/..', './backups/', '/backups/'),
            ('/temp/.', '../backups/', '/backups/'),
            ('/temp/..', 'backups/', '/backups/'),
            ('/temp/this.tar', '.gz', '/temp/this.tar/.gz'),
            ('/temp/source', '_destination', '/temp/source/_destination'),
            ('/temp/destination.txt', '_compressed.zip', '/temp/destination.txt/_compressed.zip'),
            ('/temp/destination.txt', '_copy_one', '/temp/destination.txt/_copy_one'),
            ('//node/share', 'new', '//node/share/new'),
            ('/var/log/app/temp/../archive', '', '/var/log/app/archive/'),
            ('Desktop', '../../michael/Desktop', '../michael/Desktop'),
            )
        for initial, add, result in test_data:
            start = Path(initial)
            start *= add
            self.assertEqual(start, Path(result), "%r * %r (%s) != %r" % (initial, add, start, Path(result)))

    if os.path.__name__ == 'ntpath':
        def test_nt_multiplication(self):
            "check path fusing"
            test_data = (
                ('c:','/temp/','c:/temp/'),
                ('c:','temp/','c:temp/'),
                ('c:/','/','c:/'),
                ('','/','/'),
                ('c:/','temp/','c:/temp/'),
                ('c:/','/temp/','c:/temp/'),
                ('c:/temp/','backups/','c:/temp/backups/'),
                ('c:/temp/','./backups/','c:/temp/backups/'),
                ('c:/temp/','/backups/','c:/backups/'),
                ('c:/temp/this/./.tar','../backup/./.gz','c:/temp/backup/.tar.gz'),
                ('c:/temp/../','./backups/','c:/backups/'),
                ('c:/temp/..','./backups/','c:/backups/'),
                ('c:/temp/..','./backups/','c:/backups/'),
                ('c:/temp/..','backups/','c:/backups/'),
                ('c:/temp/this.tar','.gz','c:/temp/this.tar.gz'),
                ('c:/temp/source','_destination','c:/temp/source_destination'),
                ('c:/temp/destination.txt','_compressed.zip','c:/temp/destination_compressed.txt.zip'),
                ('c:/temp/destination.txt','_copy_one','c:/temp/destination_copy_one.txt'),
                )
            for initial, add, result in test_data:
                start = Path(initial)
                start *= add
                self.assertEqual(start, Path(result), "%r * %r (%s) != %r" % (initial, add, start, Path(result)))

    if os.path.__name__ == 'posixpath':
        def test_posix_multiplication(self):
            "check path fusing"
            test_data = (
                ('c:','/temp/','/temp/'),
                ('c:','temp/','c:/temp/'),
                ('c:/','/','/'),
                ('','/','/'),
                ('c:/','temp/','c:/temp/'),
                ('c:/','/temp/','/temp/'),
                ('c:/temp/','backups/','c:/temp/backups/'),
                ('c:/temp/','./backups/','c:/temp/backups/'),
                ('c:/temp/','/backups/','/backups/'),
                ('c:/temp/this/./.tar','../backup/./.gz','c:/temp/this/backup/.gz'),
                ('c:/temp/../','./backups/','c:/backups/'),
                ('c:/temp/..','./backups/','c:/backups/'),
                ('c:/temp/.','../backups/','c:/backups/'),
                ('c:/temp/..','backups/','c:/backups/'),
                ('c:/temp/this.tar','.gz','c:/temp/this.tar/.gz'),
                ('c:/temp/source','_destination','c:/temp/source/_destination'),
                ('c:/temp/destination.txt','_compressed.zip','c:/temp/destination.txt/_compressed.zip'),
                ('c:/temp/destination.txt','_copy_one','c:/temp/destination.txt/_copy_one'),
                )
            for initial, add, result in test_data:
                start = Path(initial)
                start *= add
                self.assertEqual(start, Path(result), "%r * %r (%s) != %r" % (initial, add, start, Path(result)))

    def test_division(self):
        "check path division"
        self.assertEqual(Path('c:') / Path('/temp/'), Path('c:/temp/'))
        self.assertEqual(Path('c:/') / Path('/temp/'), Path('c:/temp/'))
        self.assertEqual(Path('c:/temp/') / Path('backups/'), Path('c:/temp/backups/'))
        self.assertEqual(Path('c:/temp/') / Path('/backups/'), Path('c:/temp/backups/'))
        self.assertEqual(Path('c:/temp/') / Path('source'), Path('c:/temp/source'))
        self.assertEqual(Path('c:/temp/source') / Path('destination'), Path('c:/temp/source/destination'))
        self.assertEqual(Path('c:/temp/destination') / Path('.txt'), Path('c:/temp/destination/.txt'))
        self.assertEqual(Path('c:/temp/destination.txt') / Path('copy_one'), Path('c:/temp/destination.txt/copy_one'))
        self.assertEqual(Path('hello') / Path('/temp/'), Path('hello/temp/'))
        self.assertEqual(Path('') / Path('/temp/'), Path('/temp/'))
        self.assertEqual(Path('temp') / Path(''), Path('temp/'))

    def test_subtraction(self):
        "check path subtraction"
        self.assertEqual(Path('/temp') - Path('/temp'), Path(''))
        self.assertEqual(Path('/temp/backups') - Path(''), Path('/temp/backups'))
        self.assertEqual(Path('/temp/backups') - Path('/'), Path('temp/backups'))
        self.assertEqual(Path('/temp/backups') - Path('/temp'), Path('/backups'))
        self.assertEqual(Path('/temp/backups') - Path('/temp/'), Path('backups'))
        self.assertEqual(Path('/temp/backups') - Path('/temp/backups'), Path(''))
        self.assertEqual(Path('/temp/destination.txt') - Path(''), Path('/temp/destination.txt'))
        self.assertEqual(Path('/temp/destination.txt') - Path('/temp'), Path('/destination.txt'))
        self.assertEqual(Path('/temp/destination.txt') - Path('/temp/'), Path('destination.txt'))
        self.assertEqual(Path('/temp/destination.txt') - Path('/temp/destination'), Path('.txt'))
        self.assertEqual(Path('//machine/share/some/path/and/file.txt') - Path('//machine/share/some/path/'), Path('and/file.txt'))
        self.assertEqual(Path('/usr/local/bin') - Path(''), Path('/usr/local/bin'))
        self.assertEqual(Path('//machine/share/some/path/and/file.txt') - Path(''), Path('//machine/share/some/path/and/file.txt'))

    if os.path.__name__ == 'ntpath':
        def test_win_subtraction(self):
            "check path subtraction"
            self.assertEqual(Path('c:/temp') - Path('c:/temp'), Path(''))
            self.assertEqual(Path('c:/temp') - Path('c:'), Path('/temp'))
            self.assertEqual(Path('c:/temp') - Path('c:/'), Path('temp'))
            self.assertEqual(Path('c:/temp/backups') - Path('c:'), Path('/temp/backups'))
            self.assertEqual(Path('c:/temp/backups') - Path('c:/'), Path('temp/backups'))
            self.assertEqual(Path('c:/temp/backups') - Path('c:/temp'), Path('/backups'))
            self.assertEqual(Path('c:/temp/backups') - Path('c:/temp/'), Path('backups'))
            self.assertEqual(Path('c:/temp/backups') - Path('c:/temp/backups'), Path(''))
            self.assertEqual(Path('c:/temp/destination.txt') - Path(''), Path('c:/temp/destination.txt'))

    if py_ver < (3, 0):
        def test_marshall(self):
            from xmlrpclib import dumps, loads
            self.assertEqual(Path('/home/ethan/'), loads(dumps(((Path('/home/ethan/'),))))[0][0])
            self.assertEqual(Path(b'/home/ethan/'), loads(dumps((Path(b'/home/ethan/'),)))[0][0])
            if py3_mode:
                self.assertNotEqual(Path(u'/home/ethan/'), loads(dumps((Path(u'/home/ethan/'),)))[0][0])
            else:
                self.assertEqual(Path(u'/home/ethan/'), loads(dumps((Path(u'/home/ethan/'),)))[0][0])
    else:
        def test_marshall(self):
            from xmlrpc.client import dumps, loads
            self.assertEqual(Path(b'/home/ethan/'), loads(dumps((Path(b'/home/ethan/'),)))[0][0].data)
            self.assertEqual(Path(u'/home/ethan/'), loads(dumps((Path(u'/home/ethan/'),)))[0][0])
            self.assertEqual(Path('/home/ethan/'), loads(dumps((Path('/home/ethan/'),)))[0][0])

class TestPathStringMethods(TestCase):

    def setUp(self):
        self.bp_log = Path('/var/log/syslog'.encode('ascii'))
        self.up_log = Path(unicode('/var/log/syslog'))
        self.bp_file = Path('/home/ethan/Desktop/Downloads/delta_game.tar.gz'.encode('ascii'))
        self.up_file = Path(unicode('/home/ethan/Desktop/Downloads/delta_game.tar.gz'))
        self.bp_ext = Path('/home/ethan/.bashrc'.encode('ascii'))
        self.up_ext = Path(unicode('/home/ethan/.bashrc'))
        self.b_slash = '/'.encode('ascii')
        self.u_slash = unicode('/')
        self.b_D = 'D'.encode('ascii')
        self.u_D = unicode('D')
        self.b_dot = '.'.encode('ascii')
        self.u_dot = unicode('.')
        self.b_gz = 'gz'.encode('ascii')
        self.u_gz = unicode('gz')
        self.b_log = 'log'.encode('ascii')
        self.u_log = unicode('log')
        self.b_rc = 'rc'.encode('ascii')
        self.u_rc = unicode('rc')

    def test_count(self):
        self.assertEqual(self.bp_log.count(self.b_slash), 3)
        self.assertEqual(self.up_log.count(self.u_slash), 3)
        self.assertEqual(self.bp_file.count(self.b_D), 2)
        self.assertEqual(self.up_file.count(self.u_D), 2)
        self.assertEqual(self.bp_ext.count(self.b_dot), 1)
        self.assertEqual(self.up_ext.count(self.u_dot), 1)

    def test_endswith(self):
        self.assertTrue(self.bp_log.endswith(self.b_log))
        self.assertFalse(self.bp_log.endswith(self.b_gz))
        self.assertTrue(self.bp_file.endswith(self.b_gz))
        self.assertFalse(self.bp_file.endswith(self.b_rc))
        self.assertTrue(self.bp_ext.endswith(self.b_rc))
        self.assertFalse(self.bp_ext.endswith(self.b_log))
        self.assertTrue(self.up_log.endswith(self.u_log))
        self.assertFalse(self.up_log.endswith(self.u_gz))
        self.assertTrue(self.up_file.endswith(self.u_gz))
        self.assertFalse(self.up_file.endswith(self.u_rc))
        self.assertTrue(self.up_ext.endswith(self.u_rc))
        self.assertFalse(self.up_ext.endswith(self.u_log))

    def test_find(self):
        self.assertEqual(self.bp_log.find(self.b_slash), 0)
        self.assertEqual(self.bp_file.find(self.b_slash), 0)
        self.assertEqual(self.bp_ext.find(self.b_slash), 0)
        self.assertEqual(self.bp_log.find(self.b_D), -1)
        self.assertEqual(self.bp_file.find(self.b_D), 12)
        self.assertEqual(self.bp_ext.find(self.b_D), -1)
        self.assertEqual(self.bp_log.find(self.b_dot), -1)
        self.assertEqual(self.bp_file.find(self.b_dot), 40)
        self.assertEqual(self.bp_ext.find(self.b_dot), 12)
        self.assertEqual(self.up_log.find(self.u_slash), 0)
        self.assertEqual(self.up_file.find(self.u_slash), 0)
        self.assertEqual(self.up_ext.find(self.u_slash), 0)
        self.assertEqual(self.up_log.find(self.u_D), -1)
        self.assertEqual(self.up_file.find(self.u_D), 12)
        self.assertEqual(self.up_ext.find(self.u_D), -1)
        self.assertEqual(self.up_log.find(self.u_dot), -1)
        self.assertEqual(self.up_file.find(self.u_dot), 40)
        self.assertEqual(self.up_ext.find(self.u_dot), 12)

    def test_format(self):
        self.assertRaises(AttributeError, self.bp_file.format, "{!s}")
        self.assertRaises(AttributeError, self.up_file.format, "{!s}")

    def test_format_map(self):
        self.assertRaises(AttributeError, self.bp_log.format, "{!s}")
        self.assertRaises(AttributeError, self.up_log.format, "{!s}")

    def test_index(self):
        self.assertEqual(self.bp_log.find(self.b_slash), 0)
        self.assertEqual(self.bp_file.find(self.b_slash), 0)
        self.assertEqual(self.bp_ext.find(self.b_slash), 0)
        self.assertRaises(ValueError, self.bp_log.index, self.b_D)
        self.assertEqual(self.bp_file.find(self.b_D), 12)
        self.assertRaises(ValueError, self.bp_ext.index, self.b_D)
        self.assertRaises(ValueError, self.bp_log.index, self.b_dot)
        self.assertEqual(self.bp_file.find(self.b_dot), 40)
        self.assertEqual(self.bp_ext.find(self.b_dot), 12)
        self.assertEqual(self.up_log.find(self.u_slash), 0)
        self.assertEqual(self.up_file.find(self.u_slash), 0)
        self.assertEqual(self.up_ext.find(self.u_slash), 0)
        self.assertRaises(ValueError, self.up_log.index, self.u_D)
        self.assertEqual(self.up_file.find(self.u_D), 12)
        self.assertRaises(ValueError, self.up_ext.index, self.u_D)
        self.assertRaises(ValueError, self.up_log.index, self.u_dot)
        self.assertEqual(self.up_file.find(self.u_dot), 40)
        self.assertEqual(self.up_ext.find(self.u_dot), 12)

    def test_lstrip(self):
        self.assertEqual(self.bp_log.lstrip(self.b_slash), self.bp_log[1:])
        self.assertEqual(self.bp_file.lstrip(self.b_slash), self.bp_file[1:])
        self.assertEqual(self.bp_ext.lstrip(self.b_slash), self.bp_ext[1:])
        self.assertEqual(self.up_log.lstrip(self.u_slash), self.up_log[1:])
        self.assertEqual(self.up_file.lstrip(self.u_slash), self.up_file[1:])
        self.assertEqual(self.up_ext.lstrip(self.u_slash), self.up_ext[1:])

    def test_replace(self):
        self.assertEqual(
                self.bp_log.replace(self.b_slash, self.b_rc),
                self.bp_log[:].replace(self.b_slash, self.b_rc),
                )
        self.assertEqual(
                self.bp_file.replace(self.b_dot, self.b_rc),
                self.bp_file[:].replace(self.b_dot, self.b_rc),
                )
        self.assertEqual(
                self.bp_ext.replace(self.b_rc, self.b_log),
                self.bp_ext[:].replace(self.b_rc, self.b_log),
                )
        self.assertEqual(
                self.up_log.replace(self.u_slash, self.u_rc),
                self.up_log[:].replace(self.u_slash, self.u_rc),
                )
        self.assertEqual(
                self.up_file.replace(self.u_dot, self.u_rc),
                self.up_file[:].replace(self.u_dot, self.u_rc),
                )
        self.assertEqual(
                self.up_ext.replace(self.u_rc, self.u_log),
                self.up_ext[:].replace(self.u_rc, self.u_log),
                )

    def test_rstrip(self):
        self.assertEqual(self.bp_log.rstrip(self.b_log), self.bp_log[:-3])
        self.assertEqual(self.bp_file.rstrip(self.b_gz), self.bp_file[:-2])
        self.assertEqual(self.bp_ext.rstrip(self.b_rc), self.bp_ext[:-2])
        self.assertEqual(self.up_log.rstrip(self.u_log), self.up_log[:-3])
        self.assertEqual(self.up_file.rstrip(self.u_gz), self.up_file[:-2])
        self.assertEqual(self.up_ext.rstrip(self.u_rc), self.up_ext[:-2])

    def test_startswith(self):
        self.assertTrue(self.bp_log.endswith(self.b_log))
        self.assertFalse(self.bp_log.endswith(self.b_rc))
        self.assertTrue(self.bp_file.endswith(self.b_gz))
        self.assertFalse(self.bp_file.endswith(self.b_log))
        self.assertTrue(self.bp_ext.endswith(self.b_rc))
        self.assertFalse(self.bp_ext.endswith(self.b_gz))
        self.assertTrue(self.up_log.endswith(self.u_log))
        self.assertFalse(self.up_log.endswith(self.u_rc))
        self.assertTrue(self.up_file.endswith(self.u_gz))
        self.assertFalse(self.up_file.endswith(self.u_log))
        self.assertTrue(self.up_ext.endswith(self.u_rc))
        self.assertFalse(self.up_ext.endswith(self.u_gz))

    def test_strip(self):
        self.assertEqual(self.bp_log.strip(self.b_slash + self.b_log), self.bp_log[1:-3])
        self.assertEqual(self.bp_file.strip(self.b_slash + self.b_gz), self.bp_file[1:-2])
        self.assertEqual(self.bp_ext.strip(self.b_slash + self.b_rc), self.bp_ext[1:-2])
        self.assertEqual(self.up_log.strip(self.u_slash + self.u_log), self.up_log[1:-3])
        self.assertEqual(self.up_file.strip(self.u_slash + self.u_gz), self.up_file[1:-2])
        self.assertEqual(self.up_ext.strip(self.u_slash + self.u_rc), self.up_ext[1:-2])

    def test_strip_ext(self):
        self.assertEqual(self.bp_log.strip_ext(), self.bp_log)
        self.assertEqual(self.bp_file.strip_ext(), self.bp_file[:-3])
        self.assertEqual(self.bp_file.strip_ext(2), self.bp_file[:-7])
        self.assertEqual(self.bp_file.strip_ext(3), self.bp_file[:-7])
        self.assertEqual(self.bp_ext.strip_ext(), self.bp_ext[:-7])
        self.assertEqual(self.up_log.strip_ext(), self.up_log)
        self.assertEqual(self.up_file.strip_ext(), self.up_file[:-3])
        self.assertEqual(self.up_file.strip_ext(2), self.up_file[:-7])
        self.assertEqual(self.up_file.strip_ext(3), self.up_file[:-7])
        self.assertEqual(self.up_ext.strip_ext(), self.up_ext[:-7])


class TestPathFileOperations(TestCase):

    def setUp(self):
        os.mkdir(tempdir)
        self.dirs = ['project', 'project/audio', 'project/graphics', 'project/app']
        self.files = [
                '.sh', 'project/INSTALL', 'project/README', 'project/audio/sound.mp3',
                'project/graphics/background.png', 'project/app/LICENSE',
                ]
        self.project_dirs = ['audio', 'graphics', 'app']
        self.project_files = ['INSTALL', 'README', 'audio/sound.mp3', 'graphics/background.png', 'app/LICENSE']
        self.sh_file = os.path.join(tempdir, '.sh')
        self.project = os.path.join(tempdir, 'project')
        self.project_audio = os.path.join(tempdir, 'project', 'audio')
        self.project_graphics = os.path.join(tempdir, 'project', 'graphics')
        self.project_app = os.path.join(tempdir, 'project', 'app')
        self.project_install = os.path.join(tempdir, 'project', 'INSTALL')
        self.project_readme = os.path.join(tempdir, 'project', 'README')
        self.project_audio_sound = os.path.join(tempdir, 'project', 'audio', 'sound.mp3')
        self.project_graphics_background = os.path.join(tempdir, 'project', 'graphics', 'background.png')
        self.project_app_license = os.path.join(tempdir, 'project', 'app', 'LICENSE')
        self.sh = '#!/usr/bin/sh\n#\n# just a test'
        self.readme = 'Psuedo instructions here'
        self.install = 'More psuedo instructions here'
        self.sound = ''.join([chr(x) for x in range(128)]).encode('utf-8')
        self.background = ''.join([chr(x) for x in range(127, -1, -1)]).encode('utf-8')
        self.license = 'Do what you want to'
        for entry in (self.project, self.project_audio, self.project_graphics, self.project_app):
            os.mkdir(entry)
        for entry, data in (
                (self.sh_file, self.sh),
                (self.project_readme, self.readme),
                (self.project_install, self.install),
                (self.project_app_license, self.license),
                ):
            fh = open(entry, 'w')
            fh.write(data)
            fh.close()
        for entry, data in (
                (self.project_audio_sound, self.sound),
                (self.project_graphics_background, self.background)
                ):
            fh = open(entry, 'wb')
            fh.write(data)
            fh.close()

    def tearDown(self):
        shutil.rmtree(tempdir, True)

    def test_access(self):
        self.assertEqual(Path.access(self.sh_file, X_OK), os.access(self.sh_file, X_OK))
        self.assertEqual(Path(self.project).access(X_OK), os.access(self.project, X_OK))
        self.assertEqual(Path(self.project).access('README', R_OK), os.access(os.path.join(self.project, 'README'), R_OK))

    def test_ascend(self):
        for path, target in zip(
                Path('/usr/home/ethan/source/antipathy/').ascend(),
                ('/usr/home/ethan/source/antipathy', '/usr/home/ethan/source', '/usr/home/ethan', '/usr/home', '/usr', '/'),
                ):
            self.assertEqual(path, target)
            self.assertTrue(isinstance(path, Path))
        for path, target in zip(
                Path.ascend('/usr/home/ethan/source/antipathy/'),
                ('/usr/home/ethan/source/antipathy', '/usr/home/ethan/source', '/usr/home/ethan', '/usr/home', '/usr', '/'),
                ):
            self.assertEqual(path, target)
            self.assertTrue(isinstance(path, Path))

    def test_chdir(self):
        current = os.getcwd()
        def verify(new_dir):
            self.assertEqual(os.getcwd(), new_dir)
        Path.chdir(self.project)
        verify(self.project)
        Path(current).chdir()
        verify(current)
        Path(self.project).chdir('app')
        verify(os.path.join(self.project, 'app'))
        Path(current).chdir()

    if py_ver >= (2, 6) and not is_win:

        @not_implemented
        def test_chflags(self):
            pass

    if not is_win:

        def test_chmod(self):
            def verify(mode, *files):
                for f in files:
                    self.assertEqual(os.stat(f).st_mode, mode)
            sh = os.path.join(tempdir, '.sh')
            prior = os.stat(sh).st_mode
            after = prior ^ int('777', 8)
            Path.chmod(after, sh)
            verify(after, sh)
            Path.chmod(prior, [sh])
            verify(prior, sh)
            Path(sh).chmod(after)
            verify(after, sh)
            Path(tempdir).chmod(prior, '.sh*')
            verify(prior, sh)
            Path(tempdir).chmod(after, ['.sh'])
            verify(after, sh)

    if hasattr(os, 'chown'):

        @not_implemented
        def test_chown(self):
            pass

    if not is_win:

        @not_implemented
        def test_chroot(self):
            pass

    def test_copy(self):
        def verify_binary(new_dir):
            fh = open(os.path.join(new_dir, 'sound.mp3'), 'rb')
            data = fh.read()
            fh.close()
            self.assertEqual(data, self.sound)
        def verify_text(new_dir):
            for entry, stored in (
                    (os.path.join(new_dir, 'INSTALL'), self.install),
                    (os.path.join(new_dir, 'README'), self.readme),
                    ):
                fh = open(entry)
                data = fh.read()
                fh.close()
                self.assertEqual(data, stored)
        test_1 = os.path.join(tempdir, 'test_1')
        os.mkdir(test_1)
        Path.copy(self.project_audio_sound, test_1)
        verify_binary(test_1)
        test_2 = os.path.join(tempdir, 'test_2')
        os.mkdir(test_2)
        Path.copy([self.project_install, self.project_readme], test_2)
        verify_text(test_2)
        test_3 = os.path.join(tempdir, 'test_3')
        os.mkdir(test_3)
        Path(self.project_audio_sound).copy(test_3)
        verify_binary(test_3)
        test_4 = os.path.join(tempdir, 'test_4')
        os.mkdir(test_4)
        Path(self.project).copy('*E', test_4)
        Path(self.project).copy('I*', test_4)
        verify_text(test_4)
        test_5 = os.path.join(tempdir, 'test_5')
        os.mkdir(test_5)
        Path(self.project).copy(['INSTALL', 'README'], test_5)
        verify_text(test_5)

    def test_copytree(self):
        def verify_copy(new_dir):
            for entry in self.project_dirs:
                self.assertTrue(os.path.exists(os.path.join(tempdir, new_dir, entry)))
            for entry in self.project_files:
                self.assertTrue(os.path.exists(os.path.join(tempdir, new_dir, entry)))
            for entry, data in zip(
                    self.project_files,
                    (self.install, self.readme, self.sound, self.background, self.license)
                    ):
                if len(data) < 100:
                    mode = 'r'
                else:
                    mode = 'rb'
                fh = open(os.path.join(tempdir, new_dir, entry), mode)
                entry_data = fh.read()
                fh.close()
                self.assertEqual(entry_data, data)
        source = Path(self.project)
        source.copytree(os.path.join(tempdir, 'test_1'))
        verify_copy('test_1')
        Path.copytree(self.project, os.path.join(tempdir, 'test_2'))
        verify_copy('test_2')

    def test_descend(self):
        for path, target in zip(
                Path('/usr/home/ethan/source/antipathy/').descend(),
                ('/', '/usr', '/usr/home', '/usr/home/ethan', '/usr/home/ethan/source', '/usr/home/ethan/source/antipathy'),
                ):
            self.assertEqual(path, target)
            self.assertTrue(isinstance(path, Path))
        for path, target in zip(
                Path.descend('/usr/home/ethan/source/antipathy/'),
                ('/', '/usr', '/usr/home', '/usr/home/ethan', '/usr/home/ethan/source', '/usr/home/ethan/source/antipathy'),
                ):
            self.assertEqual(path, target)
            self.assertTrue(isinstance(path, Path))

    def test_exists(self):
        self.assertTrue(Path.exists(self.project_audio))
        self.assertFalse(Path.exists(os.path.join(tempdir, 'lala')))
        self.assertTrue(Path(self.project_graphics_background).exists())
        self.assertFalse(Path(os.path.join(self.project_graphics, 'blahblah')).exists())
        self.assertTrue(Path(self.project).exists('app'))
        self.assertFalse(Path(self.project_app).exists('haha'))

    def test_getcwdb(self):
        self.assertTrue(isinstance(Path.getcwdb(), Path))

    def test_getcwdu(self):
        self.assertTrue(isinstance(Path.getcwdu(), Path))

    def test_glob(self):
        if is_win:
            pattern = '*p*'
            seeking = ['graphics', 'app']
        else:
            pattern = '*A*'
            seeking = ['INSTALL', 'README']
        def verify(found, seeking):
            found = [os.path.split(f)[1] for f in found]
            self.assertEqual(set(found), set(seeking))
        verify(
                Path.glob(os.path.join(tempdir, 'project', '*')),
                ['INSTALL', 'README', 'audio', 'graphics', 'app'],
                )
        verify(
                Path(os.path.join(tempdir, 'project', 'app', '*')).glob(),
                ['LICENSE'],
                )
        verify(
                Path(os.path.join(self.project)).glob(pattern),
                seeking,
                )

    def test_isdir(self):
        self.assertTrue(Path.isdir(self.project))
        self.assertFalse(Path(self.sh_file).isdir())
        self.assertTrue(Path(self.project).isdir('app'))

    def test_isfile(self):
        self.assertTrue(Path.isfile(self.project_audio_sound))
        self.assertFalse(Path(self.project_audio).isfile())
        self.assertTrue(Path(self.project_audio).isfile('sound.mp3'))

    if not is_win:

        def test_islink(self):
            link_ee = self.sh_file
            link_er = self.sh_file + '_link'
            os.symlink(link_ee, link_er)
            self.assertTrue(Path.islink(link_er))
            self.assertFalse(Path.islink(link_ee))
            self.assertTrue(Path(link_er).islink())
            self.assertFalse(Path(link_ee).islink())
            self.assertTrue(Path(tempdir).islink('.sh_link'))
            self.assertFalse(Path(tempdir).islink('.sh'))

        @not_implemented
        def test_ismount(self):
            pass

    if hasattr(os, 'lchflags'):

        @not_implemented
        def test_lchflags(self):
            pass

    if hasattr(os, 'lchmod'):

        def test_lchmod(self):
            def verify(mode, *files):
                for f in files:
                    self.assertEqual(os.stat(f).st_mode, mode)
            sh = os.path.join(tempdir, '.sh')
            prior = os.stat(sh).st_mode
            after = prior ^ int('777', 8)
            Path.lchmod(after, sh)
            verify(after, sh)
            Path.lchmod(prior, [sh])
            verify(prior, sh)
            Path(sh).lchmod(after)
            verify(after, sh)
            Path(tempdir).lchmod(prior, '.sh*')
            verify(prior, sh)
            Path(tempdir).lchmod(after, ['.sh'])
            verify(after, sh)

    if hasattr(os, 'lchown'):

        @not_implemented
        def test_lchown(self):
            pass

    if hasattr(os.path, 'lexists'):

        def test_lexists(self):
            self.assertTrue(Path.lexists(self.project_audio))
            self.assertFalse(Path.lexists(os.path.join(tempdir, 'lala')))
            self.assertTrue(Path(self.project_graphics_background).lexists())
            self.assertFalse(Path(os.path.join(self.project_graphics, 'blahblah')).lexists())
            self.assertTrue(Path(self.project).lexists('app'))
            self.assertFalse(Path(self.project_app).lexists('haha'))

    if not is_win:

        def test_link(self):
            Path.link(self.sh_file, os.path.join(tempdir, '.sh_test_1'))
            self.assertEqual(os.stat(self.sh_file), os.stat(os.path.join(tempdir, '.sh_test_1')))
            Path(self.sh_file).link(os.path.join(tempdir, '.sh_test_2'))
            self.assertEqual(os.stat(self.sh_file), os.stat(os.path.join(tempdir, '.sh_test_2')))
            Path(tempdir).link('.sh', os.path.join(tempdir, '.sh_test_3'))
            self.assertEqual(os.stat(self.sh_file), os.stat(os.path.join(tempdir, '.sh_test_3')))

    def test_listdir(self):
        contents = os.listdir(self.project)
        self.assertEqual(Path.listdir(self.project), contents)
        self.assertEqual(Path(self.project).listdir(), contents)
        self.assertEqual(Path(tempdir).listdir('project'), contents)

    if hasattr(os, 'lstat') and hasattr(os, 'symlink'):

        def test_lstat(self):
            sh_link = os.path.join(tempdir, 'sh_link')
            os.symlink(self.sh_file, sh_link)
            self.assertTrue(
                    os.lstat(sh_link) ==
                    Path.lstat(sh_link) ==
                    Path(sh_link).lstat() ==
                    Path(tempdir).lstat('sh_link')
                    )

    if hasattr(os, 'mkfifo'):

        @not_implemented
        def test_mkfifo(self):
            pass

    def test_mkdir(self):
        Path.mkdir(os.path.join(tempdir, 'test_1'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_1')))
        Path(os.path.join(tempdir, 'test_2')).mkdir()
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_2')))
        Path(tempdir).mkdir('test_3')
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_3')))

    def test_makedirs(self):
        Path.makedirs(os.path.join(tempdir, 'test_1', 'psyche_1', 'mirage_1'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_1', 'psyche_1', 'mirage_1')))
        Path(os.path.join(tempdir, 'test_2', 'psyche_2', 'mirage_2')).makedirs()
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_2', 'psyche_2', 'mirage_2')))
        Path(tempdir).makedirs(os.path.join('test_3', 'psyche_3', 'mirage_3'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_3')))
        Path(os.path.join(tempdir, 'test_3')).makedirs(os.path.join('psyche_3', 'mirage_3'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_3')))

    def test_move(self):
        Path.move(self.sh_file, os.path.join(tempdir, 'non-sh'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'non-sh')))
        Path(tempdir).move('non-sh', os.path.join(tempdir, 'ultra-sh'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'ultra-sh')))
        Path(os.path.join(tempdir, 'ultra-sh')).move(os.path.join(tempdir, '.sh'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, '.sh')))

    def test_open(self):
        fh = Path.open(self.sh_file)
        data = fh.read()
        fh.close()
        self.assertEqual(data, self.sh)
        fh = Path(self.project_audio_sound).open('rb')
        data = fh.read()
        fh.close()
        self.assertEqual(data, self.sound)
        fh = Path(tempdir).open('.sh')
        data = fh.read()
        fh.close()
        self.assertEqual(data, self.sh)
        fh = Path(tempdir).open('test', 'w')
        fh.write('testing 1 2 3')
        fh.close()
        fh = Path(tempdir).open('test')
        data = fh.read()
        fh.close()
        self.assertEqual(data, 'testing 1 2 3')

    if not is_win:

        def test_pathconf(self):
            self.assertTrue(
                    os.pathconf('.', 'PC_NAME_MAX') ==
                    Path.pathconf('.', 'PC_NAME_MAX') ==
                    Path('.').pathconf('PC_NAME_MAX')
                    )

        def test_pathconf_names(self):
            self.assertTrue(
                    os.pathconf_names == Path.pathconf_names == Path().pathconf_names,
                    '    os: %r\n  Path: %r\nPath(): %r' %
                        (os.pathconf_names, Path.pathconf_names, Path().pathconf_names),
                    )

        def test_readlink(self):
            test_link = os.path.join(tempdir, 'test_link')
            os.symlink(self.sh_file, test_link)
            self.assertTrue(
                    os.readlink(test_link) ==
                    Path.readlink(test_link) ==
                    Path(test_link).readlink()
                    )

    def test_removedirs(self):
        os.makedirs(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3')))
        Path.removedirs(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3'))
        self.assertFalse(os.path.exists(os.path.join(tempdir, 'test_1')))
        os.makedirs(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3')))
        Path(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3')).removedirs()
        self.assertFalse(os.path.exists(os.path.join(tempdir, 'test_1')))
        os.makedirs(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3')))
        Path(os.path.join(tempdir, 'test_1')).removedirs([os.path.join('mirage_2', 'empty_3')])
        self.assertFalse(os.path.exists(os.path.join(tempdir, 'test_1')))

    def test_rename(self):
        Path.rename(self.sh_file, os.path.join(tempdir, 'non-sh'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'non-sh')))
        Path(tempdir).rename('non-sh', os.path.join(tempdir, 'ultra-sh'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'ultra-sh')))
        Path(os.path.join(tempdir, 'ultra-sh')).rename(os.path.join(tempdir, '.sh'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, '.sh')))

    def test_renames(self):
        deep_dir = os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3')
        deep_ghost = os.path.join(deep_dir, 'ghost')
        shallow_ghost = os.path.join(tempdir, 'ghost')
        os.makedirs(deep_dir)
        fh = open(deep_ghost, 'w')
        fh.write('heelo world!')
        fh.close()
        Path.renames(deep_ghost, shallow_ghost)
        self.assertFalse(os.path.exists(os.path.join(tempdir, 'test_1')))
        self.assertTrue(os.path.exists(shallow_ghost))
        os.makedirs(deep_dir)
        Path(shallow_ghost).renames(deep_ghost)
        self.assertTrue(os.path.exists(deep_ghost))
        self.assertFalse(os.path.exists(shallow_ghost))
        Path(deep_dir).renames('ghost', shallow_ghost)
        self.assertFalse(os.path.exists(os.path.join(tempdir, 'test_1')))
        self.assertTrue(os.path.exists(shallow_ghost))

    def test_rmdir(self):
        test_dir = os.path.join(tempdir, 'mirage')
        os.mkdir(test_dir)
        Path.rmdir(test_dir)
        self.assertFalse(os.path.exists(test_dir))
        os.mkdir(test_dir)
        Path(test_dir).rmdir()
        self.assertFalse(os.path.exists(test_dir))
        os.mkdir(test_dir)
        Path(tempdir).rmdir('mirage')
        self.assertFalse(os.path.exists(test_dir))

    def test_rmtree(self):
        os.makedirs(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3')))
        Path.rmtree(os.path.join(tempdir, 'test_1'))
        self.assertFalse(os.path.exists(os.path.join(tempdir, 'test_1')))
        os.makedirs(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3')))
        Path(os.path.join(tempdir, 'test_1')).rmtree()
        self.assertFalse(os.path.exists(os.path.join(tempdir, 'test_1')))
        os.makedirs(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3'))
        self.assertTrue(os.path.exists(os.path.join(tempdir, 'test_1', 'mirage_2', 'empty_3')))
        Path(tempdir).rmtree('test_1')
        self.assertFalse(os.path.exists(os.path.join(tempdir, 'test_1')))

    def test_stat(self):
        self.assertEqual(os.stat(self.sh_file), Path.stat(self.sh_file))
        self.assertEqual(os.stat(self.sh_file), Path(self.sh_file).stat())
        self.assertEqual(os.stat(self.sh_file), Path(tempdir).stat('.sh'))

    if not is_win:

        def test_statvfs(self):
            self.assertEqual(os.statvfs(self.project), Path.statvfs(self.project))
            self.assertEqual(os.statvfs(self.project), Path(self.project).statvfs())
            self.assertEqual(os.statvfs(self.project), Path(tempdir).statvfs('project'))

        def test_symlink(self):
            Path.symlink(self.sh_file, os.path.join(tempdir, '.sh_test_1'))
            self.assertTrue(os.path.islink(os.path.join(tempdir, '.sh_test_1')))
            Path(self.sh_file).symlink(os.path.join(tempdir, '.sh_test_2'))
            self.assertTrue(os.path.islink(os.path.join(tempdir, '.sh_test_2')))
            Path(tempdir).symlink('.sh', os.path.join(tempdir, '.sh_test_3'))
            self.assertTrue(os.path.islink(os.path.join(tempdir, '.sh_test_3')))

    def test_unlink(self):
        Path.unlink(self.project_audio_sound)
        self.assertFalse(os.path.exists(self.project_audio_sound))
        Path(self.project_graphics_background).unlink()
        self.assertFalse(os.path.exists(self.project_graphics_background))
        Path(tempdir).unlink('.sh')
        self.assertFalse(os.path.exists(self.sh_file))

    @not_implemented
    def test_utime(self):
        pass

    def test_walk(self):
        self.assertTrue(
                list(os.walk(self.project)) ==
                list(Path.walk(self.project)) ==
                list(Path(self.project).walk())
                ,
                '\nos: %s\nclass: %s\ninstance: %s' % (
                        list(os.walk(self.project)),
                        list(Path.walk(self.project)),
                        list(Path(self.project).walk())
                        )
                )


class TestOspath(TestCase):

        def test_ospath(self):
            class Blah(object):
              def __init__(self, path):
                self._path = path
              def __ospath__(self):
                return self._path
            self.assertEqual('/home/ethan/source', ospath(Blah('/home/ethan/source')))


if __name__ == '__main__':
    tempdir = tempfile.mkdtemp()
    shutil.rmtree(tempdir, True)
    py3_mode = False
    if sys.argv[-1] == '-3':
        antipathy.set_py3_mode()
        py3_mode = True
        sys.argv.pop()
    try:
        unittest.main()
    finally:
        shutil.rmtree(tempdir, True)
