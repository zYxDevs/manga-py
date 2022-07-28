from manga_py.provider import Provider


class EightMusesCom:
    provider = None

    def __init__(self, provider: Provider):
        self.provider = provider
        self._n = provider.http_normal().normalize_uri

    def is_images_page(self, parser) -> bool:
        return (
            self.provider.re.search(r'/\d+$', parser[0].get('href')) is not None
            if parser
            else False
        )

    def parser(self, url, selector):
        return self.provider.html_fromstring(self._n(url), selector)

    def chapters(self, parser) -> list:
        if self.is_images_page(parser):
            return [parser]
        items = []
        selector = self.provider.chapter_selector
        for i in parser:
            items += self.chapters(self.parser(i.get('href'), selector))
        return items
