#!/usr/bin/env python

import logging
import os
import subprocess
import sys

DEFAULT_ARCHS = ['armeabi-v7a', 'arm64-v8a', 'x86', 'x86_64']
NEEDED_SO_FILES = ['libjingle_peerconnection_so.so']
TARGETS = [
    'sdk/android:libwebrtc',
    'sdk/android:libjingle_peerconnection_so',
]


def _RunGN(args):
    cmd = [sys.executable, 'gn.py']
    cmd.extend(args)
    logging.debug('Running: %r', cmd)
    subprocess.check_call(cmd)


def _RunNinja(output_directory, args):
    cmd = ['ninja',
           '-C', output_directory]
    cmd.extend(args)
    logging.debug('Running: %r', cmd)
    subprocess.check_call(cmd)


def _EncodeForGN(value):
    """Encodes value as a GN literal."""
    if isinstance(value, str):
        return '"' + value + '"'
    elif isinstance(value, bool):
        return repr(value).lower()
    else:
        return repr(value)


def _GetOutputDirectory(build_dir, arch):
    """Returns the GN output directory for the target architecture."""
    return os.path.join(build_dir, arch)


def _GetTargetCpu(arch):
    """Returns target_cpu for the GN build with the given architecture."""
    if arch in ['armeabi', 'armeabi-v7a']:
        return 'arm'
    elif arch == 'arm64-v8a':
        return 'arm64'
    elif arch == 'x86':
        return 'x86'
    elif arch == 'x86_64':
        return 'x64'
    else:
        raise Exception('Unknown arch: ' + arch)


def _GetArmVersion(arch):
    """Returns arm_version for the GN build with the given architecture."""
    if arch == 'armeabi':
        return 6
    elif arch == 'armeabi-v7a':
        return 7
    elif arch in ['arm64-v8a', 'x86', 'x86_64']:
        return None
    else:
        raise Exception('Unknown arch: ' + arch)


def Build(build_dir, arch, is_debug, rtc_use_h264):
    """Generates target architecture using GN and builds it using ninja."""
    logging.info('Building: %s', arch)
    output_directory = _GetOutputDirectory(build_dir, arch)
    gn_args = {
        'target_os': 'android',
        'is_debug': is_debug,
        'rtc_include_tests': False,
        'rtc_use_h264': rtc_use_h264,
        'target_cpu': _GetTargetCpu(arch),
    }
    arm_version = _GetArmVersion(arch)
    if arm_version:
        gn_args['arm_version'] = arm_version
    gn_args_str = '--args=' + ' '.join([k + '=' + _EncodeForGN(v) for k, v in gn_args.items()])

    gn_args_list = ['gen', output_directory, gn_args_str]
    _RunGN(gn_args_list)

    ninja_args = TARGETS[:]
    _RunNinja(output_directory, ninja_args)
