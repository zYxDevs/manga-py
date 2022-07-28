from sys import stderr

from manga_py.provider import Provider
from .helpers.std import Std


class ComicoJp(Provider, Std):

    def get_chapter_index(self) -> str:
        if idx := self.re.search(r'articleNo=(\d+)', self.chapter):
            return f'{self.chapter_id}-{idx.group(1)}'
        return str(self.chapter_id)

    def get_content(self):
        if title_no := self.re.search(
            r'\.\w{2,7}/.+titleNo=(\d+)', self.get_url()
        ):
            try:
                with self.http_post(f'{self.domain}/api/getArticleList.nhn', data={
                                'titleNo': title_no.group(1)
                            }) as req:
                    images = req.json().get('result', {}).get('list', [])

                return images
            except TypeError:
                pass
        return []

    def get_manga_name(self):
        content = self.http_get(self.get_url())
        name = self.text_content_full(content, 'title')
        return name[:name.rfind('|')].strip(' \n\t\r')

    def get_chapters(self):
        # TODO: see i['freeFlg'] Y = true, W = false #19
        items = [i['articleDetailUrl'] for i in self.content if i['freeFlg'] == 'Y']
        self.log('Free chapters count: %d' % len(items), file=stderr)
        return items[::-1]

    def get_files(self):
        items = self.html_fromstring(self.chapter, '.comic-image._comicImage > img.comic-image__image')
        return [i.get('src') for i in items]

    def get_cover(self):
        pass

    def book_meta(self) -> dict:
        # todo meta
        pass


main = ComicoJp
