import json
import os
import re
from abc import ABC
from logging import info, warning
from os import path
from sys import stderr
from typing import Tuple

from .base_classes import (
    Abstract,
    Base,
    Callbacks,
    Static,
    ArchiveName,
)
from .download_methods import OnePerOneDownloader
from .fs import (
    get_temp_path,
    basename,
    remove_file_query_params,
    path_join,
    make_dirs,
    dirname,
    touch,
    get_util_home_path,
    is_file,
)
from .info import Info


class Provider(Base, Abstract, Static, Callbacks, ArchiveName, ABC):
    _volumes_count = 0
    _archive = None
    _zero_fill = False
    _with_manga_name = False
    _info = None
    _simulate = False
    _volume = None
    _show_chapter_info = False
    _save_chapter_info = False
    _save_manga_info = False
    _debug = False
    _override_name = ''
    _downloader = OnePerOneDownloader
    global_progress = None
    _state = None

    __images_cache = []

    def __init__(self, info: Info = None):
        super().__init__()
        self._state = {}
        self.re = re
        self.json = json
        self._params['temp_directory'] = get_temp_path()
        self._info = info

    def _params_parser(self, params):
        # image params
        self._set_if_not_none(self._image_params, 'crop_blank', params.get('crop_blank', False))
        self._set_if_not_none(
            self._image_params, 'crop',
            (params.get('xt', 0),
             params.get('xr', 0),
             params.get('xb', 0),
             params.get('xl', 0)),
        )
        self._image_params['no_webp'] = params.get('no_webp', False)
        # downloading params
        self._set_if_not_none(self._params, 'destination', params.get('destination', None))
        self._zero_fill = params.get('zero_fill')
        self._with_manga_name = params.get('with_manga_name')
        self._simulate = params.get('simulate')
        self._show_chapter_info = params.get('show_chapter_info', False)
        self._save_chapter_info = params.get('save_chapter_info', False)
        self._save_manga_info = params.get('save_manga_info', False)
        self._debug = params.get('debug', False)
        self._override_name = self._params.get('override_archive_name')
        if self._with_manga_name and self._override_name:
            raise RuntimeError('Conflict of parameters. Please use only --with-manga-name, or --override-archive-name')
        self._fill_arguments(params.get('arguments') or [])
        self._skip_incomplete_chapters = params.get('skip_incomplete_chapters', False)

    def process(self, url, params=None):  # Main method
        self._params['url'] = url
        params = self.__restore_params(params if isinstance(params, dict) else {})
        self.prepare_download(params)
        try:
            self.loop_chapters()
        finally:
            self.__save_params(params)

    def prepare_cf(self, url):
        response = self.http().requests(url)
        if response.status_code != 200:
            if self._flare_solver_url is None:
                self.log(f'Found status code {response.status_code}')
                if ~response.content.find(b'| Cloudflare</title>'):
                    self.log('Found Cloudflare, but --flare-solver-url param not set')
                elif self._debug:
                    with open('dump.html', 'wb') as w:
                        w.write(response.content)
                    self.log('See dump.html in your current path')
                exit(1)
            else:
                self._use_flare_solver = True
                self.log('Try use flare-solver...')

    def prepare_download(self, params=None):
        params = params or {}

        self._flare_solver_url = params.pop('flare_solver_url', None)

        self._params_parser(params)
        for i in params:
            self._params.setdefault(i, params[i])

        proxy = params.get('proxy', None)
        if proxy is not None:
            self._storage['proxies'] = {
                'http': proxy,
                'https': proxy,
            }

        if self.__manual_ua():
            self.update_ua(self._params['user_agent'])

            cookies = (c.split('=', 1) for c in self._params['cookies'])
            self.update_cookies({c[0]: c[1] for c in cookies})

        self.prepare_cf(self.get_url())
        self.prepare_cookies()

        info(f'Manga name: {self.manga_name}')
        info('Content length %d' % len(self.content))
        self.chapters = self._prepare_chapters(self.get_chapters())
        info('Chapters received (%d)' % len(self.chapters))

        if not self._params.get('reverse_downloading', False):
            self.chapters = self._storage['chapters'][::-1]

        self._storage['init_cookies'] = self._storage['cookies']

        __ua = self.http().user_agent

        self._info.set_ua(__ua)

        info('User-agent: "%s"' % __ua)

        if self._save_manga_info:
            details = self.manga_details()
            if details is not None:
                manga_info_path = path.abspath(path.join(self.get_archive_path()[0], os.pardir))
                path.isdir(manga_info_path) or os.makedirs(manga_info_path)

                with open(path.join(manga_info_path, 'info.json'), 'w') as manga_info_file:
                    manga_info_file.write(json.dumps(self.manga_details()))

            else:
                warning('No manga details was found!')
                warning('Possibly the provider has not yet been implemented to get this information')

    def _min_max_calculate(self):
        nb_chapters = len(self.chapters)
        _min = self._params.get('skip_volumes', 0)
        _max = self._params.get('max_volumes', 0)
        # Beware, 0 can also come from command line param
        _max = _max or nb_chapters
        _max = min(nb_chapters, _max + _min)
        self.chapters_count = _max - _min
        return _min, _max

    def loop_chapters(self):
        _min, _max = self._min_max_calculate()
        count = 0  # count downloaded chapters
        for idx, __url in enumerate(self.chapters[:_min], start=1):
            if self._params.get('create_empty_files', False):
                self.chapter_id = idx - 1
                _path = '%s.%s' % self.get_archive_path()
                make_dirs(dirname(_path))
                touch(_path)

            info('Skip chapter %d / %s' % (idx, __url))

        dl = self._downloader(self)

        if callable(self.global_progress):
            self.global_progress(self.chapters_count, 0, True)

        for idx, __url in enumerate(self.chapters[_min:_max], start=_min + 1):
            self.chapter_id = idx - 1
            chapter_for_json = self.chapter_for_json()
            chapter = chapter_for_json if chapter_for_json is not None else self.chapter

            if dl.already_downloaded():
                info('Skip chapter %d / %s' % (idx, chapter))
                continue
            if self._show_chapter_info:
                print(f'\n\nCurrent chapter info: {chapter}\n', file=stderr)

            count += 1

            _path = '%s.%s' % self.get_archive_path()

            self._info.add_volume(chapter, _path)

            if not self._simulate:
                self.before_download_chapter()
                dl.volume = chapter
                dl.download_chapter(self.chapter, self.get_archive_path())
                self.after_download_chapter()

                self._state['chapter_index'] = idx

            if callable(self.global_progress):
                self.global_progress(self.chapters_count, idx - _min)
            info('Processed chapter %d / %s' % (idx, chapter))

            self._wait_after_chapter()

        for idx, __url in enumerate(self.chapters[_max:], start=_max + 1):
            self.chapter_id = idx - 1
            chapter_for_json = self.chapter_for_json()
            chapter = chapter_for_json if chapter_for_json is not None else self.chapter

            info('Skip chapter %d / %s' % (idx, chapter))

        if count == 0 and not self.quiet:
            print('No new chapters found', file=stderr)

    def get_archive_path(self) -> Tuple[str, str]:
        if self._override_name:
            _path = f"{self._override_name}_{str(self.normal_arc_name(self.get_chapter_index().split('-')))}"

        else:
            # see Std
            _path = remove_file_query_params(self.get_archive_name())
        _path = self.remove_not_ascii(_path)

        if not _path:
            _path = str(self.chapter_id)

        additional_data_name = ''
        if self.http().has_error:
            additional_data_name = '.ERROR'
            self.http().has_error = False
            warning('Error processing chapter.')

        # Manga online biz use this naming scheme (see http2). Not sure if wanted
        # arc_name =  '{:0>3}-{}'.format(idx, self.get_archive_name())
        # If we want to keep it, maybe instead override self.get_archive_name ?
        arc_name = f'{_path}{additional_data_name}'

        return (
            path_join(
                self._params.get('destination', 'Manga'),
                self.name,
                arc_name
            ).replace('?', '_').replace('"', '_').replace('>', '_').replace('<', '_').replace('|', '_')  # Windows...
            , self._archive_type()
        )

    def html_fromstring(self, url, selector: str = None, idx: int = None):
        params = {}
        if isinstance(url, dict):
            params = url['params']
            url = url['url']
        return self.document_fromstring(self.http_get(url, **params), selector, idx)

    def __manual_ua(self) -> bool:
        return self._params['cookies'] and len(self._params['cookies']) and self._params['user_agent'] and len(
            self._params['user_agent'])

    def update_ua(self, ua):
        self._storage['user_agent'] = ua
        self.http().user_agent = ua
        self._info and self._info.set_ua(ua)

    def update_cookies(self, cookies):
        for k in cookies:
            self._storage['cookies'][k] = cookies[k]
            self.http_normal().cookies[k] = cookies[k]

    def before_download_file(self, idx, url):
        url = self.before_file_save(url, idx)
        filename = remove_file_query_params(basename(url))
        _path = Static.remove_not_ascii(self._image_name(idx, filename))
        _path = get_temp_path(_path)
        return _path, idx, url

    def __restore_params(self, params) -> dict:
        # issue 400
        if params.get('auto_skip_deleted', False):
            with open(self.auto_params_file, 'r') as r:
                try:
                    _content = json.loads(r.read())
                except:
                    _content = {}
            data = _content.get(self.auto_params_key, {})
            params['skip_volumes'] = data.get('skip_volumes', params.get('skip_volumes', 0))
            params['reverse_downloading'] = data.get('reverse_downloading', params.get('reverse_downloading', False))

        return params

    def __save_params(self, params):
        # issue 400
        if not params.get('auto_skip_deleted', False):
            return
        with open(self.auto_params_file, 'r') as r:
            try:
                data = json.loads(r.read())
            except:
                data = {}
        with open(self.auto_params_file, 'w') as w:
            try:
                _params = {
                    k: params[k]
                    for k in params
                    if k not in ['_raw_params', 'auto_skip_deleted']
                    and params[k] is not None
                }

                _params['skip_volumes'] = self._state.get('chapter_index', 0)
                data[self.auto_params_key] = _params
                w.write(json.dumps(data))
            except:
                self.log('Error of automatic save parameters')

    @property
    def auto_params_file(self) -> str:
        _file = path.join(get_util_home_path(), 'auto_params.json')
        if not is_file(_file):
            make_dirs(dirname(_file))
            touch(_file)
        return _file

    @property
    def auto_params_key(self) -> str:
        return f'{self.domain}|{self.manga_name}'

    # region specified data for eduhoribe/comic-builder (see https://github.com/manga-py/manga-py/issues/347)

    def chapter_details(self, chapter) -> dict:
        """
        Following the pattern specified in
        https://github.com/eduhoribe/comic-builder/blob/goshujin-sama/samples/chapter-metadata-sample.json
        """
        pass

    def manga_details(self) -> dict:
        """
        Following the pattern specified in
        https://github.com/eduhoribe/comic-builder/blob/goshujin-sama/samples/comic-metadata-sample.json
        """
        pass

    # endregion
