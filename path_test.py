import os
import unittest
import platform
import path
from path import Path

IS_WIN = platform.platform().startswith('Windows')

print path.__file__

class TestPath(unittest.TestCase):
    test_paths = (
        ("c:\\temp\\place\\somefile.abc.xyz", 
            'c:/temp/place/somefile.abc.xyz', 'c:', '/temp/place/', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("c:\\temp\\place\\somefile.abc.", 
            'c:/temp/place/somefile.abc', 'c:', '/temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("c:\\temp\\place\\somefile.abc", 
            'c:/temp/place/somefile.abc', 'c:', '/temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("c:\\temp\\place\\somefile.", 
            'c:/temp/place/somefile', 'c:', '/temp/place/', 'somefile', 'somefile', ''),
        ("c:\\temp\\place\\somefile", 
            'c:/temp/place/somefile', 'c:', '/temp/place/', 'somefile', 'somefile', ''),
        ("c:\\temp\\place\\", 
            'c:/temp/place/', 'c:', '/temp/place/', '', '', ''),
        ("c:\\.xyz", 
            'c:/.xyz', 'c:', '/', '.xyz', '', '.xyz'),
        ("c:\\temp\\.xyz", 
            'c:/temp/.xyz', 'c:', '/temp/', '.xyz', '', '.xyz'),
        ("c:/temp/place/somefile.abc.xyz", 
            'c:/temp/place/somefile.abc.xyz', 'c:', '/temp/place/', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("c:/temp/place/somefile.abc.", 
            'c:/temp/place/somefile.abc', 'c:', '/temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("c:/temp/place/somefile.abc", 
            'c:/temp/place/somefile.abc', 'c:', '/temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("c:/temp/place/somefile.", 
            'c:/temp/place/somefile', 'c:', '/temp/place/', 'somefile', 'somefile', ''),
        ("c:/temp/place/somefile", 
            'c:/temp/place/somefile', 'c:', '/temp/place/', 'somefile', 'somefile', ''),
        ("c:/temp/place/", 
            'c:/temp/place/', 'c:', '/temp/place/', '', '', ''),
        ("c:/.xyz", 
            'c:/.xyz', 'c:', '/', '.xyz', '', '.xyz'),
        ("c:/temp/.xyz", 
            'c:/temp/.xyz', 'c:', '/temp/', '.xyz', '', '.xyz'),
        ("c:temp\\place\\somefile.abc.xyz", 
            'c:temp/place/somefile.abc.xyz', 'c:', 'temp/place/', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("c:temp\\place\\somefile.abc.", 
            'c:temp/place/somefile.abc', 'c:', 'temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("c:temp\\place\\somefile.abc", 
            'c:temp/place/somefile.abc', 'c:', 'temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("c:temp\\place\\somefile.", 
            'c:temp/place/somefile', 'c:', 'temp/place/', 'somefile', 'somefile', ''),
        ("c:temp\\place\\somefile", 
            'c:temp/place/somefile', 'c:', 'temp/place/', 'somefile', 'somefile', ''),
        ("c:temp\\place\\", 
            'c:temp/place/', 'c:', 'temp/place/', '', '', ''),
        ("c:.xyz", 
            'c:.xyz', 'c:', '', '.xyz', '', '.xyz'),
        ("c:temp\\.xyz", 
            'c:temp/.xyz', 'c:', 'temp/', '.xyz', '', '.xyz'),
        ("c:temp/place/somefile.abc.xyz", 
            'c:temp/place/somefile.abc.xyz', 'c:', 'temp/place/', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("c:temp/place/somefile.abc.", 
            'c:temp/place/somefile.abc', 'c:', 'temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("c:temp/place/somefile.abc", 
            'c:temp/place/somefile.abc', 'c:', 'temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("c:temp/place/somefile.", 
            'c:temp/place/somefile', 'c:', 'temp/place/', 'somefile', 'somefile', ''),
        ("c:temp/place/somefile", 
            'c:temp/place/somefile', 'c:', 'temp/place/', 'somefile', 'somefile', ''),
        ("c:temp/place/", 
            'c:temp/place/', 'c:', 'temp/place/', '', '', ''),
        ("c:.xyz", 
            'c:.xyz', 'c:', '', '.xyz', '', '.xyz'),
        ("c:temp/.xyz", 
            'c:temp/.xyz', 'c:', 'temp/', '.xyz', '', '.xyz'),
        ("\\temp\\place\\somefile.abc.xyz", 
            '/temp/place/somefile.abc.xyz', '', '/temp/place/', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("\\temp\\place\\somefile.abc.", 
            '/temp/place/somefile.abc', '', '/temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("\\temp\\place\\somefile.abc", 
            '/temp/place/somefile.abc', '', '/temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("\\temp\\place\\somefile.", 
            '/temp/place/somefile', '', '/temp/place/', 'somefile', 'somefile', ''),
        ("\\temp\\place\\somefile", 
            '/temp/place/somefile', '', '/temp/place/', 'somefile', 'somefile', ''),
        ("\\temp\\place\\", 
            '/temp/place/', '', '/temp/place/', '', '', ''),
        ("\\.xyz", 
            '/.xyz', '', '/', '.xyz', '', '.xyz'),
        ("\\temp\\.xyz", 
            '/temp/.xyz', '', '/temp/', '.xyz', '', '.xyz'),
        ("/temp/place/somefile.abc.xyz", 
            '/temp/place/somefile.abc.xyz', '', '/temp/place/', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("/temp/place/somefile.abc.", 
            '/temp/place/somefile.abc', '', '/temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("/temp/place/somefile.abc", 
            '/temp/place/somefile.abc', '', '/temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("/temp/place/somefile.", 
            '/temp/place/somefile', '', '/temp/place/', 'somefile', 'somefile', ''),
        ("/temp/place/somefile", 
            '/temp/place/somefile', '', '/temp/place/', 'somefile', 'somefile', ''),
        ("/temp/place/", 
            '/temp/place/', '', '/temp/place/', '', '', ''),
        ("/.xyz", 
            '/.xyz', '', '/', '.xyz', '', '.xyz'),
        ("/temp/.xyz", 
            '/temp/.xyz', '', '/temp/', '.xyz', '', '.xyz'),
        ("temp\\place\\somefile.abc.xyz", 
            'temp/place/somefile.abc.xyz', '', 'temp/place/', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("temp\\place\\somefile.abc.", 
            'temp/place/somefile.abc', '', 'temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("temp\\place\\somefile.abc", 
            'temp/place/somefile.abc', '', 'temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("temp\\place\\somefile.", 
            'temp/place/somefile', '', 'temp/place/', 'somefile', 'somefile', ''),
        ("temp\\place\\somefile", 
            'temp/place/somefile', '', 'temp/place/', 'somefile', 'somefile', ''),
        ("temp\\place\\", 
            'temp/place/', '', 'temp/place/', '', '', ''),
        (".xyz", 
            '.xyz', '', '', '.xyz', '', '.xyz'),
        ("temp\\.xyz", 
            'temp/.xyz', '', 'temp/', '.xyz', '', '.xyz'),
        ("temp/place/somefile.abc.xyz", 
            'temp/place/somefile.abc.xyz', '', 'temp/place/', 'somefile.abc.xyz', 'somefile.abc', '.xyz'),
        ("temp/place/somefile.abc.", 
            'temp/place/somefile.abc', '', 'temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("temp/place/somefile.abc", 
            'temp/place/somefile.abc', '', 'temp/place/', 'somefile.abc', 'somefile', '.abc'),
        ("temp/place/somefile.", 
            'temp/place/somefile', '', 'temp/place/', 'somefile', 'somefile', ''),
        ("temp/place/somefile", 
            'temp/place/somefile', '', 'temp/place/', 'somefile', 'somefile', ''),
        ("temp/place/", 
            'temp/place/', '', 'temp/place/', '', '', ''),
        (".xyz", 
            '.xyz', '', '', '.xyz', '', '.xyz'),
        ("temp/.xyz", 
            'temp/.xyz', '', 'temp/', '.xyz', '', '.xyz'),
        ("//peer/share/temp/.xyz", 
                '//peer/share/temp/.xyz', '//peer/share', '/temp/', '.xyz', '', '.xyz'),
        ("/", 
            '/', '', '/', '', '', ''),
        )

    def test_errors(self):
        "check errors"
        self.assertRaises(ValueError, Path, 'c://test')
        self.assertRaises(ValueError, Path, 'c:/test//file.txt')
        self.assertRaises(ValueError, Path('/backups/').__div__, Path('c:/temp/'))
        self.assertRaises(ValueError, Path('/backups/file1').__div__, Path('c:/temp/'))
        self.assertRaises(ValueError, Path('/backups/').__mul__, Path('c:/temp/'))
        self.assertRaises(ValueError, Path('/../backups/').__mul__, Path('temp/'))
        self.assertRaises(ValueError, Path('/backups/').__mul__, Path('./../../temp/'))
        self.assertRaises(ValueError, Path('c:/backups').__sub__, Path('/backups/'))
        self.assertRaises(ValueError, Path('c:/backups/temp').__sub__, Path('backups/temp'))
        self.assertRaises(ValueError, Path('c:/backups.old/temp').__sub__, Path('temp.old'))
        self.assertRaises(ValueError, Path('c:/backups/temp').__sub__, Path('backups/temp'))
        self.assertRaises(ValueError, Path('c:/backups/temp').__sub__, Path('backups/temp'))
        self.assertRaises(ValueError, Path('c:/backups/temp').__sub__, Path('backups/temp'))
        self.assertRaises(ValueError, Path('c:/backups/temp.old').__sub__, Path('c:/backups.old'))
        self.assertRaises(AttributeError, Path('/some/path').format, 'this')
        self.assertRaises(AttributeError, Path('/some/path').format_map, 'this')
        self.assertRaises(TypeError, Path('/some/other/path/').endswith, set(['an','ending','or','two']))
        self.assertRaises(TypeError, Path('/some/other/path/').startswith, set(['a','start','or','two']))

    def test_paths(self):
        "check file paths"
        enum = 0
        for actual, expected, vol, dirs, filename, base, ext in self.test_paths:
            if '\\' in actual:
                sep = '\\'
            else:
                sep = None
            p = Path(actual, sep=sep)
            self.assertEqual(p, expected, "failed on iter %d --> %r != %r" % (enum, p, expected))
            self.assertEqual(p.vol, vol, "failed on iter %d --> %r != %r" % (enum, p.vol, vol))
            self.assertEqual(p.dirs, dirs, "failed on iter %d --> %r != %r" % (enum, p.dirs, dirs))
            self.assertEqual(p.filename, filename, "failed on iter %d --> %r != %r" % (enum, p.filename, filename))
            self.assertEqual(p.base, base, "failed on iter %d --> %r != %r" % (enum, p.base, base))
            self.assertEqual(p.ext,  ext, "failed on iter %d --> %r != %r" % (enum, p.ext, ext))
            enum += 1

    def test_os_path_join(self):
        "check os.path.join"
        if IS_WIN:
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

    def test_multiplication(self):
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
            ('c:/temp/','/backups/','c:/temp/backups/'),
            ('c:/temp/this/./.tar','../backup/./.gz','c:/temp/backup/.tar.gz'),
            ('c:/temp/../','/./backups/','c:/backups/'),
            ('c:/temp/this.tar','.gz','c:/temp/this.tar.gz'),
            ('c:/temp/source','_destination','c:/temp/source_destination'),
            ('c:/temp/destination.txt','_compressed.zip','c:/temp/destination_compressed.txt.zip'),
            ('c:/temp/destination.txt','_copy_one','c:/temp/destination_copy_one.txt'),
            ('//node/share','new','//node/share/new'),
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

    def test_subtraction(self):
        "check path subtraction"
        self.assertEqual(Path('c:/temp') - Path('c:/temp'), Path(''))
        self.assertEqual(Path('c:/temp') - Path('/temp'), Path('c:'))
        self.assertEqual(Path('c:/temp') - Path('c:'), Path('/temp'))
        self.assertEqual(Path('c:/temp') - Path('c:/'), Path('temp'))
        self.assertEqual(Path('c:/temp/backups') - Path('c:'), Path('/temp/backups'))
        self.assertEqual(Path('c:/temp/backups') - Path('c:/'), Path('temp/backups'))
        self.assertEqual(Path('c:/temp/backups') - Path('c:/temp'), Path('/backups'))
        self.assertEqual(Path('c:/temp/backups') - Path('c:/temp/'), Path('backups'))
        self.assertEqual(Path('c:/temp/backups') - Path('c:/temp/backups'), Path(''))
        self.assertEqual(Path('c:/temp/backups.old') - Path('backups'), Path('c:/temp/.old'))
        self.assertEqual(Path('c:/temp/backups.old') - Path('.old'), Path('c:/temp/backups'))
        self.assertEqual(Path('c:/temp/backups.old') - Path('/temp/.old'), Path('c:backups'))
        self.assertEqual(Path('c:/temp/backups.old') - Path('c:backups'), Path('/temp/.old'))
        self.assertEqual(Path('c:/temp/destination.txt') - Path(''), Path('c:/temp/destination.txt'))


if __name__ == '__main__':
    unittest.main()
