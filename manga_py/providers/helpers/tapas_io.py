from manga_py.meta import repo_url
from manga_py.provider import Provider


class TapasIo:
    provider = None

    def __init__(self, provider: Provider):
        self.provider = provider

    def _content(self, content):
        type = content.get('type', None)
        if type == 'DEFAULT':
            return self._type_default(content)

    def _error(self, content):
        self.provider.log(
            f"\r\nERROR!\r\nCode: {content['code']}\r\nType: {content['type']}\r\nPlease, send url to developer ({repo_url})"
        )

    def _type_default(self, content):
        items = self.provider.document_fromstring(content.get('data', {}).get('html', '<html></html>'), '.art-image')
        return [i.get('src') for i in items]

    def chapter_url(self):
        return f"{self.provider.domain}/episode/view/{self.provider.chapter['id']}"

    def parse_chapter_content(self):
        content = self.provider.json.loads(self.provider.http_get(self.chapter_url()))
        if content['code'] != 200:
            self._error(content)
            return []
        _content = self._content(content)
        if _content is None:
            self._error(content)
        return _content
