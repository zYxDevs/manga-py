from manga_py.provider import Provider
from .helpers.std import Std


class CatMangaOrg(Provider, Std):
    _build_id = None

    @property
    def _content(self) -> dict:
        return self.content.get('props', {}).get('pageProps', {}).get('series', {})

    def get_archive_name(self) -> str:
        return self.normal_arc_name({
            'vol': str(self.chapter.get('volume')),
            'ch': str(self.chapter.get('number'))},
        )

    def get_chapter_index(self) -> str:
        return self.chapter_for_json()

    def get_content(self):
        url = self.re.search(r'(https?://.+?/series/[^/]+)', self.get_url()).group(1)
        return self.json.loads(
            self.re.search(
                r'>(\{"(?:query|props|page|buildId|isFallback|gsp)"\:\{.+?\})<',
                self.http_get(url),
                self.re.MULTILINE,
            ).group(1),
        )

    def _url_manga_name(self):
        return self._get_name(r'/series/([^/]+)')

    def get_manga_name(self) -> str:
        titles = self._content.get('alt_titles', [])
        return titles[0] if len(titles) > 0 else self._url_manga_name()

    def get_chapters(self):
        return self._content.get('chapters', [])[::-1]

    def get_files(self):
        # https://catmanga.org/_next/data/<buildId>/series/<name>/<number>.json
        data = self.json.loads(self.http_get(
            '{}/_next/data/{}/series/{}/{}.json'.format(
                self.domain,
                self.content.get('buildId'),
                self.content.get('query', {}).get('series') or self._url_manga_name(),
                self.chapter.get('number', 0)
            )
        ))
        return data.get('pageProps', {}).get('pages')

    def get_cover(self) -> str:
        return self._content.get('cover_art', {}).get('source', '')

    def chapter_for_json(self) -> str:
        number = self.chapter.get('number')
        volume = self.chapter.get('volume')

        return f'{number}-{volume}' if volume is not None else str(number)


main = CatMangaOrg
