from manga_py.provider import Provider
from .helpers.std import Std


class AsmHentaiCom(Provider, Std):

    def get_archive_name(self) -> str:
        return 'archive'

    def get_chapter_index(self) -> str:
        return '0'

    def get_content(self):
        return self.http_get(self.get_url())

    def get_manga_name(self) -> str:
        title = self.text_content_full(self.content, '.info > h1,title')
        if ~title.find(' Page '):
            title = self.re.search(r'(.+) Page ', title).group(1)
        return title

    def get_chapters(self):
        url = self.get_url()
        if ~url.find('/g/'):
            url = self._elements('.gallery > div > a')[0].get('href')
        return [url]

    def get_files(self):
        content = self.http_get(self.chapter)
        src = self.re.search(r'\$\(\[[\'"]//(.+)/[\'"]', content).group(1)
        pages = self.re.search(r'var +Pages ?=.*?(\d+)', content).group(1)
        http = self.re.search('(https?):', self.get_url()).group(1)
        return [f'{http}://{src}/{1 + i}.jpg' for i in range(int(pages))]

    def get_cover(self) -> str:
        return self._cover_from_content('.cover > a > img')

    def book_meta(self) -> dict:
        pass


main = AsmHentaiCom
