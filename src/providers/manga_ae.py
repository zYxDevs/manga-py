from src.provider import Provider
from .helpers.std import Std


class MangaAe(Provider, Std):

    def get_archive_name(self) -> str:
        return 'vol_{:0>3}'.format(self.get_chapter_index())

    def get_chapter_index(self) -> str:
        return self.re.search(r'\.ae/[^/]+/(\d+)', self.get_current_chapter()).group(1)

    def get_main_content(self):
        return self.http_get('{}/{}/'.format(self.get_domain(), self.get_manga_name()))

    def get_manga_name(self) -> str:
        return self.re.search(r'\.ae/([^/]+)', self.get_url()).group(1)

    def get_chapters(self):
        return self._chapters('li > a.chapter')

    def get_files(self):
        img_selector = '#showchaptercontainer img'
        parser = self.html_fromstring(self.get_current_chapter())
        pages = parser.cssselect('#morepages a + a')
        images = self._images_helper(parser, img_selector)
        if pages:
            for i in pages:
                parser = self.html_fromstring(i.get('href'))
                images += self._images_helper(parser, img_selector)
        return images

    def get_cover(self) -> str:
        return self._cover_from_content('img.manga-cover')


main = MangaAe