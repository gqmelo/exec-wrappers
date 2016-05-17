import glob

import os
import stat
import sys


def main():
    import sys
    _main(sys.argv[1:])


def _main(raw_args):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', type=str, required=True,
                        help='The type of the wrapper. Possible values: conda, schroot')
    parser.add_argument('-b', '--bin-dir', type=str, required=False,
                        help='Directory with the original executable files')
    parser.add_argument('-f', '--files-to-wrap', type=str, required=False,
                        help='List of files separated by colon (:). If given only wrappers for '
                             'files listed here will be created')
    parser.add_argument('-d', '--dest-dir', type=str, required=True,
                        help='Directory where the wrappers will be created')

    conda_group = parser.add_argument_group('conda')
    conda_group.add_argument('--conda-env-dir', type=str,
                             help='The path to the conda environment. E.g. ~/miniconda/envs/foo')
    schroot_group = parser.add_argument_group('schroot')
    schroot_group.add_argument('--schroot-name', type=str,
                               help='Name of an existing schroot or session')

    args = parser.parse_args(raw_args)

    wrapper_type = args.type
    if wrapper_type not in ['conda', 'schroot']:
        print('Invalid wrapper type: {}'.format(wrapper_type))
        parser.print_usage()

    if args.files_to_wrap:
        files_to_wrap = args.files_to_wrap.split(':')
    else:
        files_to_wrap = list_executable_files(args.bin_dir)

    if wrapper_type == 'conda':
        if not args.conda_env_dir:
            print('Missing conda argument: --conda-env-dir')
            parser.print_usage()
            exit(1)
        create_conda_wrappers(files_to_wrap, args.dest_dir, args.conda_env_dir)
    elif wrapper_type == 'schroot':
        if not args.schroot_name:
            print('Missing schroot argument: --schroot-name')
            parser.print_usage()
            exit(1)
        create_schroot_wrappers(files_to_wrap, args.dest_dir, args.schroot_name)
    else:
        print('Invalid wrapper type: {}'.format(wrapper_type))
        parser.print_usage()
        exit(1)


def create_conda_wrappers(files_to_wrap, destination_dir, conda_env_dir):
    os.path.exists(destination_dir) or os.makedirs(destination_dir)

    this_dir = os.path.dirname(__file__)

    run_in_template_filename = os.path.join(this_dir, 'templates', 'conda', 'run-in' +
                                            get_wrapper_extension())
    _create_wrappers(
        files_to_wrap,
        destination_dir,
        run_in_template_filename,
        lambda content: content.replace('@CONDA_ENV_DIR@', conda_env_dir),
    )


def create_schroot_wrappers(files_to_wrap, destination_dir, schroot_name):
    os.path.exists(destination_dir) or os.makedirs(destination_dir)

    run_in_template_filename = os.path.join(get_templates_dir(), 'schroot', 'run-in' +
                                            get_wrapper_extension())
    _create_wrappers(
        files_to_wrap,
        destination_dir,
        run_in_template_filename,
        lambda content: content.replace('@CHROOT@', schroot_name),
    )


def get_templates_dir():
    this_dir = os.path.dirname(__file__)
    return os.path.join(this_dir, 'templates')


def get_wrapper_extension():
    if sys.platform == 'win32':
        return '.bat'
    else:
        return ''


def _create_wrappers(files_to_wrap, destination_dir, run_in_template_filename, template_func):
    os.path.exists(destination_dir) or os.makedirs(destination_dir)

    with open(run_in_template_filename, 'r') as f:
        content = template_func(f.read())

    run_in_filename = os.path.join(destination_dir, 'run-in' + get_wrapper_extension())
    with open(run_in_filename, 'w') as f:
        f.write(content)
    os.chmod(run_in_filename, os.stat(run_in_filename).st_mode | stat.S_IXUSR)

    for filename in files_to_wrap:
        basename = os.path.basename(filename)
        if basename == 'run-in' + get_wrapper_extension():
            continue
        destination_filename = get_wrapper_full_path(destination_dir, basename)
        content = get_wrapper_template().format(run_in_file=run_in_filename,
                                         wrapped_file=filename)
        with open(destination_filename, 'w') as f:
            f.write(content)

        os.chmod(destination_filename, os.stat(destination_filename).st_mode | stat.S_IXUSR)


def get_wrapper_full_path(destination_dir, basename):
    if sys.platform == 'win32':
        basename = os.path.splitext(basename)[0]
    return os.path.join(destination_dir, basename + get_wrapper_extension())


def get_wrapper_template():
    if sys.platform == 'win32':
        return '''@echo off
{run_in_file} {wrapped_file} %*'''
    else:
        return '''#!/bin/sh
{run_in_file} {wrapped_file} "$@"
'''


def list_executable_files(directory):
    return sorted([
        f
        for f
        in glob.glob(directory + '/*')
        if is_executable(f)
    ])


def is_executable(filename):
    if os.path.isdir(filename):
        return False
    if sys.platform == 'win32':
        return os.path.splitext(filename)[1] in ['.bat', '.exe']
    else:
        return os.access(filename, os.X_OK)
