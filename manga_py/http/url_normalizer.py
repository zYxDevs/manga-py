from urllib.parse import urlparse


class UrlNormalizer:

    @staticmethod
    def _parse_sheme(parse, base_parse):
        uri = parse.scheme or base_parse.scheme
        return f'{uri}://'

    @staticmethod
    def _parse_netloc(parse, base_parse):
        return parse.netloc or base_parse.netloc

    @staticmethod
    def _test_path_netloc(parse):
        if parse.path.find('://') == 0:
            return urlparse(f'http{parse.path}').path
        return parse.path

    @staticmethod
    def __parse_rel_path(parse, base_parse):
        path = ''
        if base_parse.path.rfind('/') > 0:
            path = base_parse.path[:base_parse.path.rfind('/')]
        return path.rstrip('/') + '/' + parse.path.lstrip('/')

    @staticmethod
    def _parse_path(parse, base_parse):
        if parse.netloc:
            return parse.path
        if not (_path := UrlNormalizer._test_path_netloc(parse)):
            return base_parse.path
        if _path.find('/') == 0:
            return _path
        else:
            return UrlNormalizer.__parse_rel_path(parse, base_parse)

    @staticmethod
    def _parse_query(parse):
        return f'?{parse.query}' if parse.query else ''

    @staticmethod
    def _parse_fragment(parse):
        return f'#{parse.fragment}' if parse.fragment else ''

    @staticmethod
    def url_helper(url: str, base_url: str) -> str:
        parse = urlparse(url)
        base_parse = urlparse(base_url)
        un = UrlNormalizer
        sheme = un._parse_sheme(parse, base_parse)
        netloc = un._parse_netloc(parse, base_parse)
        path = un._parse_path(parse, base_parse)
        query = un._parse_query(parse)
        fragment = un._parse_fragment(parse)
        return sheme + netloc + path + query + fragment


normalize_uri = UrlNormalizer.url_helper
