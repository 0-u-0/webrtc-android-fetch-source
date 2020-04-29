#!/usr/bin/env python

import logging
import os
import subprocess
import sys

DEFAULT_ARCHS = ['armeabi-v7a', 'arm64-v8a', 'x86', 'x86_64']
TARGETS = [
    'sdk/android:libjingle_peerconnection_so',
]


def IsRealDepotTools(path):
    expanded_path = os.path.expanduser(path)
    return os.path.isfile(os.path.join(expanded_path, 'gclient.py'))


def add_depot_tools_to_path(source_dir=''):
    """Search for depot_tools and add it to sys.path."""
    # First, check if we have a DEPS'd in "depot_tools".
    deps_depot_tools = os.path.join(source_dir, 'third_party', 'depot_tools')
    if IsRealDepotTools(deps_depot_tools):
        # Put the pinned version at the start of the sys.path, in case there
        # are other non-pinned versions already on the sys.path.
        sys.path.insert(0, deps_depot_tools)
        return deps_depot_tools

    # Then look if depot_tools is already in PYTHONPATH.
    for i in sys.path:
        if i.rstrip(os.sep).endswith('depot_tools') and IsRealDepotTools(i):
            return i
    # Then look if depot_tools is in PATH, common case.
    for i in os.environ['PATH'].split(os.pathsep):
        if IsRealDepotTools(i):
            sys.path.append(i.rstrip(os.sep))
            return i
    # Rare case, it's not even in PATH, look upward up to root.
    root_dir = os.path.dirname(os.path.abspath(__file__))
    previous_dir = os.path.abspath(__file__)
    while root_dir and root_dir != previous_dir:
        i = os.path.join(root_dir, 'depot_tools')
        if IsRealDepotTools(i):
            sys.path.append(i)
            return i
        previous_dir = root_dir
        root_dir = os.path.dirname(root_dir)
    logging.error('Failed to find depot_tools')
    return None


def _RunGN(args):
    logging.info('Gn args : %s', args)

    cmd = [sys.executable, os.path.join(add_depot_tools_to_path(), 'gn.py')]
    cmd.extend(args)
    logging.debug('Running: %r', cmd)
    subprocess.check_call(cmd)


def _RunNinja(output_directory, args):
    logging.info('Ninja args : %s', args)

    cmd = [os.path.join(add_depot_tools_to_path(), 'ninja'),
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
