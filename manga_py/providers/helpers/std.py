import re
from logging import error
from time import sleep
from typing import Optional

from requests import get


class Std:
    _download_cookies = None
    _download_headers = None

    def _elements(self, selector, content=None) -> list:
        if not content:
            content = self.content
        return self.document_fromstring(content, selector)

    def _cover_from_content(self, selector, attr='src') -> Optional[str]:
        image = self._elements(selector)
        if image is not None and len(image):
            return self.normalize_uri(image[0].get(attr))
        return ''

    @staticmethod
    def _first_select_options(parser, selector, skip_first=True) -> list:
        options = 'option + option' if skip_first else 'option'
        if select := parser.cssselect(selector):
            return select[0].cssselect(options)
        return []

    @classmethod
    def _images_helper(cls, parser, selector, attr='src', alternative_attr='data-src') -> list:
        image = parser.cssselect(selector)
        images = []
        for i in image:
            src = i.get(attr) or i.get(alternative_attr)
            images.append(src.strip(' \r\n\t\0'))
        return images

    @classmethod
    def _idx_to_x2(cls, idx, default=0) -> list:
        return [
            str(idx[0]),
            str(default if len(idx) < 2 or not idx[1] else idx[1])
        ]

    @staticmethod
    def _join_groups(idx, glue='-') -> str:
        result = [i for i in idx if i]
        return glue.join(result)

    def _get_name(self, selector, url=None) -> str:
        if url is None:
            url = self.get_url()
        return re.search(selector, url)[1]

    def _get_content(self, tpl, domain=None, manga_name=None, name=None, **kwargs) -> str:
        """
        :param tpl:
        :param domain:
        :param manga_name:
        :param name:
        :param kwargs:
        :return:
        """
        try:
            return self.http_get(tpl.format(
                domain=(domain or self.domain),
                manga_name=(manga_name or self.manga_name),
                name=(name or self.name),
                **kwargs
            ))
        except Exception:
            return self.http_get(tpl.format(self.domain, self.manga_name))

    def _base_cookies(self, url=None):
        if url is None:
            url = self.get_url()
        cookies = self.http().get_base_cookies(url)
        self._storage['cookies'] = cookies.get_dict()

    def parse_background(self, image) -> str:
        url = re.search(
            r'background.+?url\([\'"]?([^\s]+?)[\'"]?\)',
            image.get('style')
        )
        return self.normalize_uri(url[1])

    def text_content_full(self, content, selector, idx: int = 0, strip: bool = True) -> Optional[str]:
        doc = self.document_fromstring(content, selector)
        return self.element_text_content_full(doc[idx], strip) if doc else None

    def element_text_content_full(self, element, strip: bool = True) -> str:
        text = element.text_content()
        if strip:
            text = text.strip()
        return text

    def text_content(self, content, selector, idx: int = 0, strip: bool = True) -> Optional[str]:
        doc = self.document_fromstring(content, selector)
        return self.element_text_content(doc[idx], strip) if doc else None

    def element_text_content(self, element, strip: bool = True) -> str:
        text = element.text
        if strip:
            text = text.strip()
        return text

    def _download(self, file_name, url, method):
        # clean file downloader
        cookies = self._download_cookies or {}
        headers = self._download_headers or {}

        now_try_count = 0
        while now_try_count < 5:
            with open(file_name, 'wb') as out_file:
                now_try_count += 1
                response = get(url, timeout=60, allow_redirects=True, headers=headers, cookies=cookies)
                if response.status_code >= 400:
                    error(f'ERROR! Code {response.status_code}\nUrl: {url}')
                    sleep(2)
                    continue
                out_file.write(response.content)
                response.close()
                out_file.close()
                break

    @staticmethod
    def _test_url(url: str, path: str = None) -> bool:
        _path = r'https?://.+?\.\w{2,7}'
        if path is not None:
            _path += path
        _re = re.compile(_path)
        return _re.search(url) is not None
