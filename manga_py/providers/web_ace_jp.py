from manga_py.provider import Provider
from .helpers.std import Std


class WebAceJp(Provider, Std):
    @staticmethod
    def remove_not_ascii(value):
        return value

    def get_archive_name(self) -> str:
        idx = self.get_chapter_index().split('-', 2)
        return self.normal_arc_name(idx)

    def get_chapter_index(self) -> str:
        idx = self.re.search(
            r'第(.+?)?話(?:-(.+?))?',
            self.chapter[1]
        )
        return self._join_groups(idx.groups()) if idx else self.chapter[1]

    def __url(self):
        return f'{self.domain}/youngaceup/contents/{self.__idx()}/'

    def __idx(self):
        return self.re.search(
            r'/contents/(\d+)',
            self.get_url()
        ).group(1)

    def get_content(self):
        return self.http_get(self.__url())

    def get_manga_name(self) -> str:
        return self.text_content_full(self.content, '.credit h1')

    def get_chapters(self):
        content = self.http_get(f'{self.__url()}episode/')
        selector = '.media:not(.yudo) > a.navigate-right'
        items = []
        n = self.normalize_uri
        for el in self._elements(selector, content):
            title = el.cssselect('.media-body p')[0]
            title = title.text_content_full().strip(' \n\r\t\0')
            items.append((n(el.get('href')), title))
        return items

    def get_files(self):
        n = self.normalize_uri
        with self.http().get(f'{self.chapter[0]}/json/') as resp:
            items = resp.json()
        return [n(i) for i in items]

    def get_cover(self) -> str:
        return self._cover_from_content('#sakuhin-info img')

    def book_meta(self) -> dict:
        # todo meta
        pass

    def chapter_for_json(self):
        return self.chapter[0]


main = WebAceJp
