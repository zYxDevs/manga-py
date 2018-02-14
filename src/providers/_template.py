from src.provider import Provider
# from .helpers.std import Std


class _Template(Provider):
# class _Template(Provider, Std):

    def get_archive_name(self) -> str:
        pass

    def get_chapter_index(self) -> str:
        pass

    def get_main_content(self):
        pass

    def prepare_cookies(self):  # if site with cookie protect
        pass

    def get_manga_name(self) -> str:
        return ''

    def get_chapters(self):  # call once
        # return self._chapters('a.chapter')
        return []

    def get_files(self):  # call ever volume loop
        return []

    def get_cover(self) -> str:
        pass
        # return self._cover_from_content('.cover img')


main = _Template
