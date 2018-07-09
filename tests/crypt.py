import unittest
from pathlib import Path
from .base import root_path
from manga_py.provider import Provider
from manga_py.crypt import AcQqComCrypt
from manga_py.crypt import KissMangaComCrypt
from manga_py.crypt import MangaRockComCrypt
from manga_py.crypt import ManhuaGuiComCrypt
from manga_py.image import Image
import json
import re


class Crypt(unittest.TestCase):
    _ac_qq_data = '8eyJjb21pYyI6eyJpZCI6NTM2NDM1LCJ0aXRsZSI6Ilx1NTczMFx1ODVjZlx1OWY1MFx1NTkyOSIsImNvbGxlY3QiOiIxNDg3OTU1IiwiaXNKYXBhbkNvbWljIjpmYWxzZSwiaXNMaWdodE5vdmVsIjpmYWxzZSwiaXNMaWdodENvbWljIjpmYWxzZSwiaXNGaW5pc2giOmZhbHNlLCJpc1JvYXN0YWJsZSI6dHJ1ZSwiZUlkIjoiS2xCUFMwTlBYVlZhQWdZZkFRWUFBd3NNSEVKWVhTZz0ifSwiY2hhcHRlciI6eyJjaWQiOjI3NCwiY1RpdGxlIjoiMTI1XHVmZjFhXHU3OGE3XHU5MWNlXHUwMGI3XHU4NTg3XHU1YzlhIFx1NGUwYSIsImNTZXEiOiIyNTUiLCJ2aXBTdGF0dXMiOjIsInByZXZDaWQiOjI3MywibmV4dENpZCI6Mjc1LCJibGFua0ZpcnN0IjoxLCJjYW5SZWFkIjpmYWxzZX0sInBpY3R1cmUiOlt7InBpZCI6IjI4MDM3Iiwid2lkdGgiOjkwMCwiaGVpZ2h0IjoxMjczLCJ1cmwiOiJodHRwczpcL1wvbWFuaHVhLnFwaWMuY25cL21hbmh1YV9kZXRhaWxcLzBcLzI1XzE2XzI0X2U5NTNiZjhhMTBjODA1MWQxNTQyYzA0OWQ0OTdlOTJhXzI4MDM3LmpwZ1wvMCJ9XSwiYWRzIjp7InRvcCI6IiIsImxlZnQiOltdLCJib3R0b20iOnsidGl0bGUiOiJcdTRlMDdcdTRlOGJcdTRlMDdcdTcwNzUiLCJwaWMiOiJodHRwczpcL1wvbWFuaHVhLnFwaWMuY25cL29wZXJhdGlvblwvMFwvMDVfMTFfNDRfYzlhZGZlZGQxMjExNjczNTAyMWEyMmJjYTY2YWVkNDFfMTUzMDc2MjI2NjYxNy5qcGdcLzAiLCJ1cmwiOiJodHRwOlwvXC9hYy5xcS5jb21cL0NvbWljXC9jb21pY0luZm9cL2lkXC82MzEzOTkiLCJ3aWR0aCI6IjY1MCIsImhlaWdodCI6IjExMCJ9fSwiYXJ0aXN0Ijp7ImF2YXRhciI6Imh0dHA6XC9cL3RoaXJkcXEucWxvZ28uY25cL2c/Yj1zZGsmaz03dmg2WVBhSUQzNWRaQzZXMkppYlBFZyZzPTY0MCZ0PTE1MTczNzA2MjkiLCJuaWNrIjoiXHVmZjA4XHU1MTZiXHU1ZWE2XHVmZjA5XHU0ZTAwXHU0ZThjXHU1ZGU1XHU0ZjVjXHU1YmE0IiwidWluQ3J5cHQiOiJkMnRQZG5WV05GZE9XVms5In19'
    _kissmanga_data = [
        'hkJ+EJR/9dCEuATq4edqK2Y2yYuk7oHv6DtMcKdZDztGw8Bdrm3Uh9Z6aZnJeq51IeU04EwWn8DUZ3wEfdvMnYtQh7GSoWdOkdJa7Dbyfs7AspTURTDMhBqYsoZzduP7kyxQ/ftwtbQ733ShihZvNUg4pcR36H4YAKEAcwhZNA0=',
        'hkJ+EJR/9dCEuATq4edqK9GZCq4jAmbydCinAnz3hV01EBnqDvmVlxgEsScYB6JxDM99fJN636C/8+qLQnGVZSDaZ5rRIISuamFvWwZBkpHl2UPXxHd/wIRd6CEcBxer6Zs7vjyjx6W33bVh1OHzeFcXJo8eHQCBmOdWEuF61fk=',
        'hkJ+EJR/9dCEuATq4edqKzJtiFoZ4A6if1KVpaBlajzEcGnP+nT58dQpi9VyyFZduSlPLh9JhUtwrnN7SGjkTCaCr12oRm+OsHRJYhcLVjsz/tcnHEeBFUCJUC9IU5mK1ZKiIDQhEHbnJzh1P+WuNirvKIrHJGwpU7+NfxDvva4=',
    ]

    @property
    def _provider(self):
        provider = Provider()
        provider._params['url'] = 'http://example.org'
        return provider

    def test_ac_qq_com(self):
        lib = AcQqComCrypt(self._provider)
        'data from ac.qq.com/ComicView/index/id/536435/cid/274'
        self.assertIsNotNone(lib.decode(self._ac_qq_data).get('comic', None))

    def test_ac_qq_com_none(self):
        lib = AcQqComCrypt(self._provider)
        self.assertIsNone(lib.decode(self._ac_qq_data[5:]).get('comic', None))

    def test_kissmanga(self):
        lib = KissMangaComCrypt()
        'view-source:kissmanga.com/Manga/Kou-1-Desu-ga-Isekai-de-Joushu-Hajimemashita/Chapter-019?id=401994'
        key = lib.decode_escape(r'\x6E\x73\x66\x64\x37\x33\x32\x6E\x73\x64\x6E\x64\x73\x38\x32\x33\x6E\x73\x64\x66')
        iv = b'a5e8e2e9c2721be0a84ad660c472c1f3'
        for i in self._kissmanga_data:
            href = lib.decrypt(iv, key, i).decode('utf-8').replace('\x10', '').replace('\x0f', '')
            self.assertEqual(href[:4], 'http')

    def test_manga_rock_com(self):
        crypt = MangaRockComCrypt()
        path_cr = Path(root_path).joinpath('files', 'manga_rock_com.mri').resolve()
        path_test = Path(root_path).joinpath('temp', 'manga_rock_com').resolve()

        self.assertIsNone(Image.real_extension(path_cr))

        with open(path_cr, 'rb') as r:
            with open(path_test, 'wb') as w:
                w.write(crypt.decrypt(r.read()))

        self.assertIsNotNone(Image.real_extension(path_test))

    def test_manhuagui_com(self):
        lib = ManhuaGuiComCrypt()
        'view-source:https://www.manhuagui.com/comic/28271/375550.html#p=3'
        with open(Path(root_path).joinpath('files', 'manhuagui')) as f:
            js = re.search(r'\](\(function\(.+\))\s?<', f.read())
            data = lib.decrypt(js.group(1), '')
            js = re.search(r'\(({.+})\)', data).group(1)
            js = json.loads(js)
        # self.assertIs(js, dict)  # NOT WORKED Oo
        self.assertTrue(isinstance(js, dict))