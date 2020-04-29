#!/usr/bin/env python
import os
import argparse
import logging
import sys
import shutil

SDK_PATH = '/sdk/android'
JAVA_SOURCE_PATH = '/java'


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
    parser = argparse.ArgumentParser(description='fetch android java source and libraries.')
    parser.add_argument('--source-dir',
                        help='WebRTC source dir. Example: /realpath/to/src')
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Debug logging.')
    return parser.parse_args()


def _FetchJavaSource(source_dir):
    if not source_dir:
        logging.error("no source dir")
        return
    sdk_dir = source_dir + SDK_PATH

    if not os.path.isdir(sdk_dir):
        logging.error("unknown dir : " + sdk_dir)
        return

    # create java source dir if not exists
    java_dir = os.path.abspath(os.getcwd()) + JAVA_SOURCE_PATH
    if not os.path.isdir(java_dir):
        os.mkdir(java_dir)

    # remove legacy file
    _RemoveFiles(java_dir)

    _CopyFiles(sdk_dir + '/api', java_dir)

    _CopyFiles(sdk_dir + '/src/java', java_dir)

    # fetch java sour


def main():
    args = _ParseArgs()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    _FetchJavaSource(args.source_dir)


if __name__ == '__main__':
    sys.exit(main())
