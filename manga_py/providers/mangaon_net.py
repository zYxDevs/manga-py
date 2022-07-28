from manga_py.provider import Provider
from .helpers.std import Std


class MangaOnNet(Provider, Std):
    __has_ch = False

    def get_archive_name(self) -> str:
        idx = self.get_chapter_index().split('-')
        var = {'vol': idx[0], 'ch': idx[1]} if self.__has_ch else {'vol': idx}
        return self.normal_arc_name(var)

    def get_chapter_index(self) -> str:
        selector = r'(?:vol-?(\d+))?(?:-ch-?(\d+))'
        ch = self.chapter
        re = self.re.search(selector, ch)
        if re:
            self.__has_ch = True
            re = re.groups()
            return f'{re[0] or 0}-{re[1]}'
        selector = r'.+-(\d+)'
        re = self.re.search(selector, ch)
        return f'0-{re.group(1)}'

    def get_content(self):
        url = f'{self.domain}/manga-info/{self.manga_name}'
        return self.http_get(url)

    def get_manga_name(self) -> str:
        url = self.get_url()
        if ~url.find('read-online'):
            url = self.html_fromstring(url, '.back-info a', 0).get('href')
        return self.re.search(r'/manga-info/([^/]+)', url).group(1)

    def get_chapters(self):
        return self._elements('.list-chapter li > a')

    def get_files(self):
        items = self.html_fromstring(self.chapter, '#list-img img')
        return [i.get('src') for i in items]

    def get_cover(self) -> str:
        return self._cover_from_content('.cover img')

    def book_meta(self) -> dict:
        # todo meta
        pass


main = MangaOnNet
