#!/usr/bin/env python3

import argparse
import logging
from time import ctime, time
import sys
from ass_parser import AssParser
from font_loader import FontLoader
import os
from json import JSONDecoder
from subprocess import call
import cProfile
from shutil import copy2 as copyfile

default_config = { "font_dirs":[],
            "include_system_fonts":True,
            "verbose":False,
            "exclude_unused_fonts":False,
            "exclude_comments":False,
            "log_file":None}

def get_script_directory():
    return os.path.dirname(__file__)

def merge_configs(args, file, default):
    config = dict(default)
    config.update(file)
    config.update(args.__dict__)

    for key, value in config.items():
        if key not in {'output_location', 'additional_font_dirs'} and value is None:
            config[key] = file[key] if key in file and file[key] is not None else default[key]
    if config['additional_font_dirs']:
        config['font_dirs'].extend(config['additional_font_dirs'])
    return config

def get_config(args):
    with open(os.path.join(get_script_directory(), "config.json")) as file:
        file_text = file.read()
    from_file = JSONDecoder().decode(file_text)
    return merge_configs(args, from_file, default_config)

def process(args):
    config = get_config(args)

    fonts =  AssParser.get_fonts_statistics(os.path.abspath(config['script']), config['exclude_unused_fonts'], config['exclude_comments'])
    if config['rebuild_cache']:
        FontLoader.discard_cache()

    collector = FontLoader(config['font_dirs'], config['include_system_fonts'])
    found, not_found, paths = collector.get_fonts_for_list(fonts)

    if len(not_found) != 0:
        sys.exit(1)
    elif len(found) != 0:
        print(*paths, sep = "\n")
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ASS font collector")

    parser.add_argument('--include', action='append', metavar='directory', dest='additional_font_dirs', help='Additional font directory to include')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--with-system', action='store_true', dest='include_system_fonts', help='Include system fonts')
    group.add_argument('--without-system', action='store_false', dest='include_system_fonts', help='Exclude system fonts')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--exclude-comments', action='store_true', dest='exclude_comments', help='Exclude comments')
    group.add_argument('--include-comments', action='store_false', dest='exclude_comments', help='Include comments')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--exclude-unused-fonts', action='store_true', dest='exclude_unused_fonts', help='Exclude fonts without any glyphs used')
    group.add_argument('--include-unused-fonts', action='store_false', dest='exclude_unused_fonts', help='Include fonts without any glyphs used')
    parser.add_argument('--rebuild-cache', action='store_true', dest='rebuild_cache', help='Rebuild font cache')

    parser.add_argument('script', default=None, help='input script')
    parser.set_defaults(include_system_fonts = None, exclude_comments=None, exclude_unused_fonts = None,
                        verbose = None, log_file = None, rebuild_cache=False, output_location=None)
    args = parser.parse_args(sys.argv[1:])
    process(args)
