import glob

import os
import stat
import sys


def main():
    _main(sys.argv[1:])


def _main(raw_args):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', type=str, required=True,
                        help='The type of the wrapper. Possible values: conda, virtualenv,'
                             ' schroot, custom')
    parser.add_argument('-b', '--bin-dir', type=str, required=False,
                        help='Directory with the original executable files. If --files-to-wrap is'
                             ' not given, it will try to detect all executable files in this'
                             ' directory and create a wrapper for each of them. By default the'
                             ' wrapper will execute the absolute path.')
    parser.add_argument('--use-basename', action='store_true', required=False,
                        help='If given, the wrappers created with --bin-dir will execute the'
                             ' executable basename instead of the absolute path. Make sure that the'
                             ' wrappers behave appropriately as this depends on the PATH variable.')
    parser.add_argument('-f', '--files-to-wrap', type=str, required=False,
                        help='List of files separated by colon (:). If given only wrappers for'
                             ' files listed here will be created. By default the wrapper will execute'
                             ' the exact path that is passed to --files-to-wrap. If --bin-dir is'
                             ' given, it will be used as a prefix to --files-to-wrap')
    parser.add_argument('-d', '--dest-dir', type=str, required=True,
                        help='Directory where the wrappers will be created')


    conda_group = parser.add_argument_group('conda')
    conda_group.add_argument('--conda-env-dir', type=str,
                             help='The path to the conda environment. E.g. ~/miniconda/envs/foo')

    conda_group = parser.add_argument_group('virtualenv')
    conda_group.add_argument('--virtual-env-dir', type=str,
                             help='The path to the virtualenv directory')

    schroot_group = parser.add_argument_group('schroot')
    schroot_name_group = schroot_group.add_mutually_exclusive_group()
    schroot_name_group.add_argument('--schroot-name', type=str,
                                    help='Name of an existing schroot')
    schroot_name_group.add_argument('--schroot-session', type=str,
                                    help='Name of an existing schroot session')
    schroot_group.add_argument('--schroot-options', type=str,
                               help='Extra options to be passed to the schroot command. E.g.'
                                    ' --schroot-options="-p -d $HOME"')

    custom_group = parser.add_argument_group('custom')
    custom_group.add_argument('--custom-script', type=str, required=False,
                              help='This specifies a custom script which will be used to execute the'
                                   ' wrapped commands.')

    args = parser.parse_args(raw_args)

    wrapper_type = args.type
    if wrapper_type not in ['conda', 'virtualenv', 'schroot', 'custom']:
        print('Invalid wrapper type: {}'.format(wrapper_type))
        parser.print_usage()

    files_to_wrap = get_files_to_wrap(args.bin_dir, args.files_to_wrap, args.use_basename)

    # TODO: Refactor these if's
    if wrapper_type == 'conda':
        if not args.conda_env_dir:
            print('Missing conda argument: --conda-env-dir')
            parser.print_usage()
            exit(1)
        create_conda_wrappers(files_to_wrap, args.dest_dir, args.conda_env_dir)
    elif wrapper_type == 'schroot':
        if not args.schroot_name and not args.schroot_session:
            print('Missing schroot argument: should pass either --schroot-name or '
                  '--schroot-session')
            parser.print_usage()
            exit(1)
        create_schroot_wrappers(files_to_wrap, args.dest_dir, schroot_name=args.schroot_name,
                                schroot_session=args.schroot_session,
                                schroot_options=args.schroot_options)
    elif wrapper_type == 'virtualenv':
        if not args.virtual_env_dir:
            print('Missing virtualenv argument: --virtual-env-dir')
            parser.print_usage()
            exit(1)
        create_virtualenv_wrappers(files_to_wrap, args.dest_dir, args.virtual_env_dir)
    elif wrapper_type == 'custom':
        if not args.custom_script:
            print('Missing custom argument: --custom-script')
            parser.print_usage()
            exit(1)
        create_custom_wrappers(files_to_wrap, args.dest_dir, args.custom_script)
    else:
        print('Invalid wrapper type: {}'.format(wrapper_type))
        parser.print_usage()
        exit(1)


def get_files_to_wrap(bin_dir=None, specified_files_to_wrap=None, use_basename=False):
    files_to_wrap = []
    if specified_files_to_wrap:
        files_to_wrap = specified_files_to_wrap.split(':')
        if bin_dir:
            files_to_wrap = [os.path.join(bin_dir, f) for f in files_to_wrap]
    else:
        files_to_wrap = list_executable_files(bin_dir)
        if use_basename:
            files_to_wrap = [os.path.basename(f) for f in files_to_wrap]

    return files_to_wrap


def create_conda_wrappers(files_to_wrap, destination_dir, conda_env_dir):
    os.path.exists(destination_dir) or os.makedirs(destination_dir)

    this_dir = os.path.dirname(__file__)

    run_in_template_filename = os.path.join(this_dir, 'templates', 'conda', 'run-in' +
                                            get_wrapper_extension())
    _create_wrappers(
        files_to_wrap,
        destination_dir,
        run_in_template_filename,
        lambda content: content.replace('__CONDA_ENV_DIR__', conda_env_dir),
    )


def create_virtualenv_wrappers(files_to_wrap, destination_dir, virtual_env_dir):
    os.path.exists(destination_dir) or os.makedirs(destination_dir)

    this_dir = os.path.dirname(__file__)

    run_in_template_filename = os.path.join(this_dir, 'templates', 'virtualenv', 'run-in' +
                                            get_wrapper_extension())
    _create_wrappers(
        files_to_wrap,
        destination_dir,
        run_in_template_filename,
        lambda content: content.replace('__VIRTUAL_ENV__', virtual_env_dir),
    )


def create_schroot_wrappers(files_to_wrap, destination_dir, schroot_name=None,
                            schroot_session=None, schroot_options=None):
    assert schroot_name or schroot_session
    if schroot_options:
        schroot_options = schroot_options + ' '
    else:
        schroot_options = ''

    os.path.exists(destination_dir) or os.makedirs(destination_dir)

    run_in_template_filename = os.path.join(get_templates_dir(), 'schroot', 'run-in' +
                                            get_wrapper_extension())


    def create_content(content):
        if schroot_session:
            return content.replace('__CHROOT_OPTIONS__', '{}-r -c {}'.format(schroot_options, schroot_session))
        else:
            return content.replace('__CHROOT_OPTIONS__', '{}-c {}'.format(schroot_options, schroot_name))

    _create_wrappers(
        files_to_wrap,
        destination_dir,
        run_in_template_filename,
        create_content,
    )


def create_custom_wrappers(files_to_wrap, destination_dir, custom_script):
    if not is_executable(custom_script):
        raise ValueError('Custom script "{}" is not an executable')

    os.path.exists(destination_dir) or os.makedirs(destination_dir)

    _create_wrappers(
        files_to_wrap,
        destination_dir,
        custom_script,
        lambda content: content,
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
