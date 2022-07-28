from abc import abstractmethod, ABCMeta


class ArchiveName(metaclass=ABCMeta):
    _vol_fill = False

    @abstractmethod
    def get_chapter_index(self):
        pass

    def get_archive_name(self) -> str:
        idx = self.get_chapter_index()
        self._vol_fill = True
        return self.normal_arc_name({'vol': idx.split('-')})

    def normal_arc_name(self, idx) -> str:
        if isinstance(idx, (str, int)):
            idx = [idx]
        if isinstance(idx, list):
            self._vol_fill = True
            return self.__normal_name_list(idx)
        if isinstance(idx, dict):
            return self.__normal_name_dict(idx)
        raise DeprecationWarning(f'Wrong arc name type: {type(idx)}')

    def __normal_name_dict(self, idx: dict) -> str:
        vol = idx.get('vol')
        ch = idx.get('ch')
        result = ''
        if vol:
            if isinstance(vol, str):
                vol = [vol]
            result = self.__normal_name_list(vol)
        if ch:
            if vol:
                result += '-'
            result += f'ch_{self.__fill(ch)}'

        if self._with_manga_name:
            name = self._params.get('name', '')
            if not len(name):
                name = self.manga_name

            result = f'{name}-{result}'

        return result

    def __normal_name_list(self, idx: list) -> str:
        fmt = 'vol_{:0>3}'
        if len(idx) > 1:
            fmt += '-{}' * (len(idx) - 1)
        elif self._vol_fill and self._zero_fill:
            idx.append('0')
            fmt += '-{}'
        return fmt.format(*idx)

    @staticmethod
    def __fill(var, fmt: str = '-{}') -> str:
        if isinstance(var, str):
            var = [var]
        return (fmt * len(var)).format(*var).lstrip('-')
