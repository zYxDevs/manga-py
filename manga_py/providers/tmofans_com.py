from manga_py.provider import Provider
from .helpers.std import Std
from sys import stderr
from manga_py.meta import repo_url


class TmoFansCom(Provider, Std):
    def get_chapter_index(self) -> str:
        try:
            re = self.re.compile(r'Capítulo (\d+(?:\.\d+)?)')
            return re.search(self.chapter[0]).group(1).replace('.', '-')
        except IndexError as e:
            self.log(
                f'\nNot found chapter index.\nURL: {self.get_url()}\nChapter: {self.chapter[0]}\nPlease, report this bug: {repo_url}/issues/new?template=bug_report.md\n',
                file=stderr,
            )


            raise e

    def get_content(self):
        return self.http_get(self.get_url())

    def get_manga_name(self) -> str:
        return self._get_name(r'/manga/\d+/([^/]+)')

    def get_chapters(self):
        raw_chapters = self._elements('.list-group .upload-link')
        n = self.normalize_uri
        re = self.re.compile(r'(.+/)')
        chapters = []
        for i in raw_chapters:
            try:
                text = i.cssselect('.btn-collapse')[0].text_content_full()
                link = i.cssselect('.list-group .list-group-item .row a')[-1]
            except IndexError:
                self.log('Error extract chapter', file=stderr)
                continue
            request_url = n(link.get('href'))
            response = self.http().requests(request_url, method='head')
            url = n(re.search(response.headers['Location']).group(1))
            chapters.append((text, f'{url}cascade'))

        return chapters

    def get_files(self):
        url = self.chapter[1]
        parser = self.html_fromstring(url)
        return self._images_helper(parser, 'img.viewer-image')

    def get_cover(self) -> str:
        return self._cover_from_content('.book-thumbnail')

    def chapter_for_json(self) -> str:
        return self.chapter[1]


main = TmoFansCom
