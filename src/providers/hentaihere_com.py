from src.provider import Provider
from .helpers.std import Std


class HentaiHereCom(Provider, Std):
    __local_storage = None
    _cdn = 'https://hentaicdn.com/hentai'

    def get_archive_name(self) -> str:
        idx = self.get_chapter_index().split('-')
        return '{}-{}'.format(*self._idx_to_x2(idx))

    def get_chapter_index(self) -> str:
        chapter = self.get_current_chapter()
        idx = self.re.search('/m/[^/]+/([^/]+(?:/[^/]+))', chapter)
        return idx.group(1).replace('/', '-')

    def get_main_content(self):
        if self.__local_storage is None:
            url = self.re.search('(/m/[^/]+)', self.get_url())
            url = '{}{}'.format(self.get_domain(), url.group(1))
            self.__local_storage = self.http_get(url)
        return self.__local_storage

    def get_manga_name(self) -> str:
        content = self.get_main_content()
        selector = 'span.hide[itemscope] span[itemprop="name"]'
        name = self.document_fromstring(content, selector)
        if not name:
            selector = '#detail span[itemprop="title"]'
            name = self.document_fromstring(content, selector)
        return name[0].text_content().strip()

    def get_chapters(self):
        return self._elements('ul.arf-list > li > a')

    def get_files(self):
        chapter = self.get_current_chapter()
        content = self.http_get(chapter)
        items = self.re.search(r'_imageList\s*=\s*(\[".+"\])', content).group(1)
        return [self._cdn + i for i in self.json.loads(items)]

    def get_cover(self) -> str:
        return self._cover_from_content('#cover img')


main = HentaiHereCom
