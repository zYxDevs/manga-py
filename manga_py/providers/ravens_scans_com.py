from .gomanga_co import GoMangaCo
from .helpers.std import Std


class RavensScansCom(GoMangaCo, Std):
    _name_re = '/(?:serie|read)/([^/]+)'
    __api_url = '/lector/api/v2/comic?stub='

    def get_content(self):
        url = f'{self.domain}{self.__api_url}{self.manga_name}'
        with self.http().get(url) as resp:
            return resp.json().get('languages', [])

    def get_chapters(self):
        items = []
        for i in self.content:
            url = f'{self.domain}{self.__api_url}{self.manga_name}&lang={i}'
            with self.http().get(url) as resp:
                items += resp.json().get('chapters', [])
        return [i.get('href') for i in items[::-1]]  # DON'T TOUCH THIS!

    def get_cover(self) -> str:
        return self.content.get('fullsized_thumb_url', None)


main = RavensScansCom
