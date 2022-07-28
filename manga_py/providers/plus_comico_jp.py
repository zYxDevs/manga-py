from time import time
from urllib import parse

from manga_py.crypt.puzzle import Puzzle
from manga_py.fs import rename
from manga_py.provider import Provider
from .helpers.std import Std


class PlusComicoJp(Provider, Std):
    scrambles = []

    def get_chapter_index(self) -> str:
        return self.re.search('/store/\d+/(\d+)', self.chapter).group(1)

    def get_content(self):
        if content := self._storage.get('main_content', None):
            return content
        idx = self.re.search('/store/(\d+)', self.get_url())
        url = f'{self.domain}/store/{idx.group(1)}/'
        return self.http_get(url)

    def get_manga_name(self) -> str:
        return self.text_content_full(self.content, 'h1 > ._title')

    def get_chapters(self):
        idx = self.re.search(r'/store/(\d+)', self.get_url()).group(1)
        with self.http().post(f'{self.domain}/store/api/getTitleArticles.nhn', data={
                'titleNo': idx
            }) as resp:
            json = resp.json()
        items = []
        for i in json.get('result', {}).get('list', {}):
            items.extend(
                m.get('articleDetailUrl')
                for m in i.get('articleList')
                if m.get('freeFlg') == 'Y'
            )

        return items

    def get_files(self):
        url = self.http().requests(self.chapter, method='head')
        location = url.headers.get('location')
        self.http().requests(location, method='head')

        location = parse.urlparse(location)
        params = parse.parse_qs(location.query)

        ts = int(time())
        base_url = '{}://{}{}/diazepam_hybrid.php?param={}&ts={}&_={}&reqtype=0'.format(
            location.scheme,
            location.netloc,
            self.re.search(r'(.+)/\w+\.php', location.path).group(1),
            parse.quote_plus(params.get('param')[0]),
            ts,
            ts + 1305,
        )

        pages_url = f'{base_url}&mode=7&file=face.xml&callback=jQ12_34'
        scramble_url = base_url + '&mode=8&file={:0>4}.xml'
        file_url = base_url + '&mode=1&file={:0>4}_0000.bin'

        total_pages = self.re.search(r'TotalPage>(\d+)</TotalPage', self.http_get(pages_url))
        total_pages = int(total_pages.group(1)) if total_pages else 0
        items = []
        self.scrambles = []
        for i in range(total_pages):
            c = self.re.search(r'Scramble>(.+?)</Scramble', self.http_get(scramble_url.format(i)))
            self.scrambles.append(c.group(1))
            items.append(file_url.format(i))
        return items

    def get_cover(self) -> str:
        return self._cover_from_content('.cover img')

    def after_file_save(self, _path: str, idx: int):
        _matrix = self.scrambles[idx].split(',')
        div_num = 4
        matrix = {int(i): n for n, i in enumerate(_matrix)}
        p = Puzzle(div_num, div_num, matrix, 8)
        p.need_copy_orig = True
        p.de_scramble(_path, f'{_path}.jpg')
        rename(f'{_path}.jpg', _path)
        return _path, None

    def save_file(self, idx=None, callback=None, url=None, in_arc_name=None):
        if in_arc_name is None:
            in_arc_name = f'{idx}_image.jpg'
        super().save_file(idx, callback, url, in_arc_name)


main = PlusComicoJp
