#!/usr/bin/env python
import os
import argparse
import logging
import sys
import shutil

from build_tools import Build

SDK_PATH = '/sdk/android'
JAVA_COPY_PATH = '/java'
JAVA_COLLECT_PATH = ['/api', '/src/java']
OUT_PATH = '/out'
ARCHS = ['armeabi-v7a', 'arm64-v8a', 'x86', 'x86_64']


def _RemoveFiles(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def _CopyFiles(src, dst):
    src_files = os.listdir(src)
    for file_name in src_files:
        if file_name != '.DS_Store':
            shutil.copytree(src + '/' + file_name, dst + '/' + file_name, dirs_exist_ok=True)


def _ParseArgs():
    parser = argparse.ArgumentParser(description='Collect and build WebRTC Android java source and libraries.')
    parser.add_argument('--source-dir',
                        help='WebRTC source dir. Example: /realpath/to/src')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Debug logging.')
    parser.add_argument('--is-debug', action='store_true', default=True,
                        help='Debug or not.')

    return parser.parse_args()


def _FetchJavaSource(source_dir):
    sdk_dir = source_dir + SDK_PATH

    if not os.path.isdir(sdk_dir):
        logging.error("unknown sdk dir : " + sdk_dir)
        return

    # create java source dir if not exists
    java_dir = os.path.abspath(os.getcwd()) + JAVA_COPY_PATH
    if not os.path.isdir(java_dir):
        os.mkdir(java_dir)

    # remove legacy file
    _RemoveFiles(java_dir)

    # collect java source
    for location in JAVA_COLLECT_PATH:
        _CopyFiles(sdk_dir + location, java_dir)


def _CollectLibraries(source_dir):
    pass


def _BuildLibraries(source_dir, is_debug):
    build_dir = source_dir + OUT_PATH
    # Build(build_dir, 'x86', is_debug, False)


def main():
    args = _ParseArgs()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if not args.source_dir:
        logging.error("no source dir")
        return -1

    _FetchJavaSource(args.source_dir)

    _BuildLibraries(args.source_dir, args.is_debug)


if __name__ == '__main__':
    sys.exit(main())
