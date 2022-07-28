from manga_py.provider import Provider
from .helpers.std import Std


class DanbooruDonmaiUs(Provider, Std):
    _is_tag = False
    _archive_prefix = 'danbooru_'
    _manga_name = None

    def get_archive_name(self) -> str:
        return 'page_{:0>2}'.format(self.chapter) if self.chapter else 'archive'

    def get_chapter_index(self) -> str:
        return str(self.chapter) if self.chapter else '0'

    def get_content(self):
        return self.http_get(self.get_url())

    def get_manga_name(self) -> str:
        if ~self.get_url().find('tags='):
            self._is_tag = True
            self._manga_name = self._get_name(r'[\?&]tags=([^&]+)')
        else:
            self._manga_name = self._get_name(r'/posts/(\d+)')
        return self._archive_prefix + self._manga_name

    def get_chapters(self):  # pragma: no cover
        if self._is_tag:
            pages = self._elements('.paginator .current-page > span')
            images_on_page = len(self._elements('#posts > div > article'))
            if pages:
                count = self.html_fromstring(
                    f'{self.domain}/counts/posts?tags={self.manga_name}',
                    '#a-posts',
                    0,
                ).text_content_full()

                page = self.re.search(r'\n\s+(\d+)', count).group(1)
                max_page = int(page) // images_on_page + 1
                if max_page > 1001:
                    self.log('1000 pages maximum!')
                    max_page = 1000
                return range(1, max_page)[::-1]
        return [1]

    def _tag_images(self):  # pragma: no cover
        url = f'{self.domain}/posts?tags={self._manga_name}&page={self.chapter}'
        parser = self.html_fromstring(url, '#posts article a')
        n = self.normalize_uri
        images = []
        for i in parser:
            images += self._post_image(n(i.get('href')))
        return images

    def _post_image(self, url):  # pragma: no cover
        parser = self.html_fromstring(url) if isinstance(url, str) else url
        if full_size := parser.cssselect('#image-resize-notice a'):
            return [full_size[0].get('href')]
        return [parser.cssselect('#image')[0].get('src')]

    def _post_images(self, url):  # pragma: no cover
        parser = self.html_fromstring(url)
        if links := parser.cssselect('#has-parent-relationship-preview article a'):
            images = []
            n = self.normalize_uri
            for i in links:
                images += self._post_image(n(i.get('href')))
            return images
        return self._post_image(parser)

    def get_files(self):
        if self._is_tag:
            return self._tag_images()
        return self._post_images(self.get_url())

    def get_cover(self) -> str:
        pass

    def book_meta(self) -> dict:
        # todo meta
        pass

    def chapter_for_json(self):
        return self.get_url()


main = DanbooruDonmaiUs
