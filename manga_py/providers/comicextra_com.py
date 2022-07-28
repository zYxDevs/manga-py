from manga_py.provider import Provider
from .helpers.std import Std


class ComicExtraCom(Provider, Std):

    def get_chapter_index(self) -> str:
        if idx := self.re.search(r'/chapter-(.+)', self.chapter):
            return f'{self.chapter_id}-{idx.group(1)}'
        return str(self.chapter_id)

    def get_content(self):
        return self._get_content('{}/comic/{}')

    def get_manga_name(self):
        url = self.get_url()
        if test := self.re.search('/comic/([^/]+)', url):
            return test.group(1)
        return self.re.search('/([^/]+)/chapter', url).group(1)

    def get_chapters(self):
        return self._elements('#list td a')

    def get_files(self):
        url = f'{self.chapter}/full'
        items = self.html_fromstring(url, '.chapter-container img.chapter_img')
        return [i.get('src') for i in items]

    def get_cover(self):
        return self._cover_from_content('.movie-image img')

    def book_meta(self) -> dict:
        # todo meta
        pass


main = ComicExtraCom
