#!/usr/bin/python3
# -*- coding: utf-8 -*-

from atexit import register as atexit_register
from json import dumps
from logging import info, warning, basicConfig, INFO, WARN, getLogRecordFactory, setLogRecordFactory
from os import makedirs, path
from shutil import rmtree
from sys import exit
from .cli.args import get_cli_arguments

from .meta import version
from .fs import get_temp_path, root_path
from .base_classes.web_driver import get_display, get_driver
from .default_config import dump_init_content
from .default_config.actions import load_config

from .fs import get_info
from .cli import Cli
from .info import Info
import better_exceptions
better_exceptions.hook()


@atexit_register
def before_shutdown():
    get_display() and get_display().stop()
    get_driver() and get_driver().close()
    temp_dir = get_temp_path()
    path.isdir(temp_dir) and rmtree(temp_dir)


def _run_util(args):
    """
    :param args:
    :return:
    :rtype Info|str
    """
    _info = Info(args)

    _info.start()
    Cli(args, _info).start()

    _info = (
        dumps(
            _info.get(),
            indent=2,
        )
        if args.get('print_json', False)
        else []
    )

    return _info


def _update_all(args):
    parse_args = args.parse_args()
    info('Update all')
    multi_info = {}

    dst = parse_args.destination
    json_info = get_info(dst)

    for i in json_info:
        parse_args.manga_name = i['manga_name']
        parse_args.url = i['url']
        _info = _run_util(args)
        multi_info[i['directory']] = _info
    parse_args.quiet or (parse_args.print_json and print(multi_info))


def run_util(args):
    """
    Main util function
    :param args:
    :return:
    """

    temp_path = get_temp_path()
    path.isdir(temp_path) or makedirs(temp_path)

    try:
        _info = _run_util(args)
        args.get('quiet', False) or (args.get('print_json', False) and print(_info))
        return 0
    except KeyboardInterrupt:
        warning('\nUser interrupt')
        return 1


__root = len(root_path())
__old_factory = getLogRecordFactory()


def __log_factory(*args, **kwargs):
    record = __old_factory(*args, **kwargs)
    record.my_pathname = record.pathname[__root:]
    record.custom_attribute = "my-attr"
    return record


def main():
    dump_init_content()

    args_ = get_cli_arguments()

    args = args_.parse_args().__dict__
    setLogRecordFactory(__log_factory)

    default_config = load_config().get_all()

    for k in args:
        if k not in default_config:
            continue

        if args[k] == args_.get_default(k):
            args[k] = default_config[k]

    log_format = '"%(levelname)s:%(my_pathname)s:%(lineno)s:%(asctime)s:%(message)s"'
    basicConfig(level=(INFO if args.get('debug', False) else WARN), format=log_format)

    if ~version.find('alpha'):
        warning('Alpha release! There may be errors!')

    exit(run_util(args))


if __name__ == '__main__':
    main()
