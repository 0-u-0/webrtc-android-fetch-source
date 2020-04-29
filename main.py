#!/usr/bin/env python
import os
import argparse
import logging
import sys
import shutil
import zipfile

from build_tools import Build

SDK_PATH = '/sdk/android'
SCRIPT_DIR = os.path.abspath(os.getcwd())
JAVA_COPY_PATH = os.path.join(SCRIPT_DIR, 'java')
LIBS_COPY_PATH = os.path.join(SCRIPT_DIR, 'jniLibs')

JAVA_COLLECT_PATH = [SDK_PATH + '/api', SDK_PATH + '/src/java', '/rtc_base/java/src']
OUT_PATH = '/out'
ARCHS = ['armeabi-v7a', 'arm64-v8a', 'x86', 'x86_64']
NEEDED_SO_FILES = ['libjingle_peerconnection_so.so']


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
            shutil.copytree(os.path.join(src, file_name), os.path.join(dst, file_name), dirs_exist_ok=True)


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
    # create java source dir if not exists
    if not os.path.isdir(JAVA_COPY_PATH):
        os.mkdir(JAVA_COPY_PATH)

    # remove legacy file
    _RemoveFiles(JAVA_COPY_PATH)

    # collect java source
    for location in JAVA_COLLECT_PATH:
        _CopyFiles(source_dir + location, JAVA_COPY_PATH)


def _CollectLibraries(build_dir):
    if not os.path.isdir(LIBS_COPY_PATH):
        os.mkdir(LIBS_COPY_PATH)

    _RemoveFiles(LIBS_COPY_PATH)

    for arch in ARCHS:
        output_directory = os.path.join(build_dir, arch)
        if os.path.isdir(output_directory):
            logging.info('Collecting: %s', arch)
            arch_dir = os.path.join(LIBS_COPY_PATH, arch)
            os.mkdir(arch_dir)

            for so_file in NEEDED_SO_FILES:
                so_file_path = os.path.join(output_directory, so_file)
                shutil.copy(so_file_path, arch_dir)


def zip_dir(path, zip_file):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip_file.write(os.path.join(root, file))


def _ZipFiles(output_file='libwebrtc.zip'):
    os.remove(output_file)
    with zipfile.ZipFile(output_file, 'w') as zip_file:
        zip_dir(os.path.basename(JAVA_COPY_PATH), zip_file)
        zip_dir(os.path.basename(LIBS_COPY_PATH), zip_file)


def _BuildLibraries(build_dir, is_debug):
    # Build(build_dir, 'x86', is_debug, False)
    return


def main():
    args = _ParseArgs()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    if not args.source_dir:
        logging.error("no source dir")
        return -1

    _FetchJavaSource(args.source_dir)

    build_dir = args.source_dir + OUT_PATH

    _BuildLibraries(build_dir, args.is_debug)

    _CollectLibraries(build_dir)

    _ZipFiles()


if __name__ == '__main__':
    sys.exit(main())
