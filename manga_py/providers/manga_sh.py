from manga_py.provider import Provider
from .helpers.std import Std


class MangaSh(Provider, Std):
    _api_url = 'https://api.manga.sh/api/v1/'
    _cdn_url = 'https://cdn.manga.sh/'

    def get_chapter_index(self) -> str:
        chapter = self.chapter
        _ch = chapter.get('ChapterNumberAbsolute', self.chapter_id)
        _vol = chapter.get('VolumeNumber', 0)
        _ch_v = chapter.get('ChapterNumberVolume', '')
        if _ch_v:
            _ch_v = f'_{_ch_v}'
        return f'{_vol}-{_ch}{_ch_v}'

    def get_content(self):
        idx = self._get_name(r'/comics/(\d+)')
        url = '{}series_chapters?query=SeriesId.Id:{}&order=asc&sortby=TimeUploaded&limit=0&offset=0'
        with self.http().get(url.format(self._api_url, idx)) as resp:
            return resp.json()

    def get_manga_name(self) -> str:
        content = self.content.get('response')[0]
        return content.get('SeriesId').get('Name')

    def get_chapters(self):
        return list(self.content.get('response', []))

    def _url_helper(self, chapter):
        return f"{self._api_url}series_chapters/{chapter.get('Hash')}"

    def get_files(self):
        url = self._url_helper(self.chapter)
        with self.http().get(url) as resp:
            items = resp.json()
        items = items.get('response', [{}])[0].get('SeriesChaptersFiles', {})
        return [self._cdn_url + i.get('Name') for i in items]

    def get_cover(self) -> str:
        content = self.content.get('response')[0]
        content = content.get('SeriesId').get('CoverImage')
        return f'{self._cdn_url}/covers/{content}'

    def book_meta(self) -> dict:
        # todo meta
        pass

    def chapter_for_json(self):
        return self._url_helper(self.chapter)


main = MangaSh
