from .hentaifox_com import HentaiFoxCom


class nHentaiNet(HentaiFoxCom):
    _idx_re = r'/g/(\d+)'
    _url_str = '{}/g/{}/'
    _name_selector = '#info h1'
    _cdn = 'https://i.nhentai.net/galleries/'
    __ext = {'j': 'jpg', 'p': 'png', 'g': 'gif'}

    def get_files(self):
        page = self._elements('#thumbnail-container a')[0]
        n = self.normalize_uri
        content = self.http_get(n(page.get('href')))
        imgs = self.re.search(r'gallery.+?JSON\.parse\("(\{.+\})', content)
        imgs = self.json.loads(imgs.group(1).encode().decode('unicode_escape'))
        idx = imgs.get('media_id')
        return [
            f"{self._cdn}{idx}/{n + 1}.{self.__ext.get(i.get('t'))}"
            for n, i in enumerate(imgs.get('images', {}).get('pages', []))
        ]

    def get_cover(self) -> str:
        return self._cover_from_content('#cover img', 'data-src')


main = nHentaiNet
