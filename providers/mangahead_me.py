#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lxml.html import document_fromstring
import re

domainUri = 'http://mangahead.me'


def get_main_content(url, get=None, post=None):
    name = get_manga_name(url)
    return get('{}/Manga-Raw-Scan/{}'.format(domainUri, name))


def get_volumes(content=None, url=None):
    parser = document_fromstring(content).cssselect('table table table a[href^="/"]')
    return [domainUri + i.get('href') for i in parser]


def get_archive_name(volume, index: int = None):
    name = re.search('\.me/(?:Manga-Raw-Scan/)?[^/]+/([^/]+)', volume)
    if not name:
        return 'vol_{:0>3}'.format(index)
    return name.groups()[0]


def get_images(main_content=None, volume=None, get=None, post=None):
    content = get(volume)
    parser = document_fromstring(content).cssselect('#main_content .mangahead_thumbnail_cell a[name]')
    if len(parser) < 1:
        return []
    _ = document_fromstring(get(domainUri + parser[0].get('href'))).cssselect('#mangahead_image')[0].get('src')
    img_uri = _[0: 1 + _.rfind('/')]
    return [img_uri + i.get('name') for i in parser]


def get_manga_name(url, get=None):
    name = re.search('\.me/(?:index.php/)?(?:Manga-\w+-Scan/)?([^/]+)', url)
    if not name:
        return ''
    return name.groups()[0]


if __name__ == '__main__':
    print('Don\'t run this, please!')
