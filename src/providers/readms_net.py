from src.provider import Provider


class ReadMsNet(Provider):

    def get_archive_name(self) -> str:
        idx = self.re.search('/r/[^/]+/([^/]+)/([^/]+)', self.get_current_chapter()).groups()
        return 'vol_{:0>3}-{}'.format(*idx)

    def get_chapter_index(self) -> str:
        idx = self.re.search('/r/[^/]+/([^/]+)', self.get_current_chapter()).group(1)
        return '{}-0'.format(idx)

    def get_main_content(self):
        name = self.get_manga_name()
        return self.http_get('{}/manga/{}'.format(self.get_domain(), name))

    def get_manga_name(self) -> str:
        return self.re.search('\\.net/(?:manga|r)/([^/]+)', self.get_url()).group(1)

    def get_chapters(self):
        items = self.document_fromstring(self.get_storage_content(), '.table-striped td > a')
        return [self.http().normalize_uri(i.get('href')) for i in items]

    def prepare_cookies(self):
        pass

    @staticmethod
    def _get_image(parser):
        items = parser.cssselect('img#manga-page')
        return items[0].get('src') if len(items) else None

    def get_files(self):
        parser = self.html_fromstring(self.get_current_chapter())
        img = self._get_image(parser)
        images = []
        img and images.append(img)
        pages = parser.cssselect('.btn-reader-page .dropdown-menu li + li a')
        for i in pages:
            parser = self.html_fromstring(self.http().normalize_uri(i.get('href')))
            img = self._get_image(parser)
            img and images.append(img)
        return images

    def _loop_callback_chapters(self):
        pass

    def _loop_callback_files(self):
        pass


main = ReadMsNet