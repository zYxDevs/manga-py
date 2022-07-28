from time import time

from manga_py.provider import Provider
from .helpers.std import Std


class ComicoCoIdTitles(Provider, Std):
    _url = None

    def get_chapter_index(self) -> str:
        return str(self.chapter.get('id', '0'))

    def _manga_id(self):
        idx = self.re.search(r'/titles/(\d+)', self.get_url())
        return idx.group(1)

    def get_content(self):
        self._url = f'{self.domain}/titles/{self._manga_id()}'
        return self.http_get(self._url)

    def get_manga_name(self) -> str:
        h2 = self.document_fromstring(self.content, '.con > h2', 0)
        return f'{h2.text_content_full()} - {self._manga_id()}'

    @staticmethod
    def __parse_page(content):
        return [
            i
            for i in content.get('data', {}).get('list', [])
            if i.get('salePolicy', {}).get('isFree', False)
        ]

    def get_chapters(self):
        items = []
        for page in range(1, 10):
            try:
                with self.http().get(f'{self._url}/chapters?page={page}&_={int(time())}') as req:
                    content = req.json()
                if content.get('header', {}).get('resultCode', -1) < 0:
                    break
                items += self.__parse_page(content)
            except Exception:
                break
        return items

    def get_files(self):
        parser = self.html_fromstring(
            f"{self._url}/chapters/{self.chapter.get('id')}", '._view', 0
        )

        return self._images_helper(parser, '._image')

    def get_cover(self) -> str:
        return self._cover_from_content('.bg_img_small img')

    def book_meta(self) -> dict:
        # todo meta
        pass


main = ComicoCoIdTitles
