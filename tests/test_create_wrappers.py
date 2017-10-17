import os
import subprocess
import stat
import sys

import pytest

from exec_wrappers import create_wrappers
from exec_wrappers.create_wrappers import list_executable_files, create_conda_wrappers, \
    create_schroot_wrappers, get_templates_dir, get_wrapper_extension


def test_list_executable_files(tmpdir):
    executable_filename = _create_executable_file(tmpdir.join('executable_filename'))

    _create_non_executable_file(tmpdir.join('non_executable'))

    assert list_executable_files(str(tmpdir)) == [str(executable_filename)]


def test_list_executable_files_sorted(tmpdir):
    filename_1 = _create_executable_file(tmpdir.join('1_executable'))
    filename_2 = _create_executable_file(tmpdir.join('j_executable'))
    filename_3 = _create_executable_file(tmpdir.join('z_executable'))

    assert list_executable_files(str(tmpdir)) == [
        str(filename_1),
        str(filename_2),
        str(filename_3)
    ]


def _create_executable_file(filepath):
    if sys.platform == 'win32':
        filepath = filepath.new(ext='bat')

    filepath.write('')
    if sys.platform != 'win32':
        filepath.chmod(filepath.stat().mode | stat.S_IXUSR)

    return filepath


def _create_non_executable_file(filepath):
    filepath.write('')
    return filepath


WRAPPER_CREATOR_AND_ARGS = [
    (create_conda_wrappers, {'conda_env_dir': 'miniconda/envs/test'}),
]
if sys.platform.startswith('linux'):
    WRAPPER_CREATOR_AND_ARGS.extend([
        (create_schroot_wrappers, {'schroot_name': 'ubuntu-14.04'}),
    ])


@pytest.mark.parametrize(('wrapper_creator', 'extra_kwargs'), WRAPPER_CREATOR_AND_ARGS)
def test_wrappers_creators(wrapper_creator, extra_kwargs, tmpdir):
    wrappers_dir = tmpdir.join('wrappers')
    bin_dir = tmpdir.join('bin')

    kwargs = {
        'files_to_wrap': [str(bin_dir.join('python')), str(bin_dir.join('gcc'))],
        'destination_dir': str(wrappers_dir),
        'inline': False,
    }
    kwargs.update(extra_kwargs)
    wrapper_creator(**kwargs)

    _check_wrappers(wrappers_dir, ['run-in', 'python', 'gcc'])


WRAPPER_TYPE_ARGS_CONTENT = [
    # The third element a string that should be present in the run-in script
    ('conda', (['--conda-env-dir', 'miniconda/envs/test']), 'miniconda/envs/test'),
    ('virtualenv', (['--virtual-env-dir', 'virtualenv/test-env']), 'virtualenv/test-env'),
]
if sys.platform.startswith('linux'):
    WRAPPER_TYPE_ARGS_CONTENT.extend([
        (
            'schroot',
            (['--schroot-name', 'ubuntu-14.04']),
            'schroot -c ubuntu-14.04 -- '
        ),
        (
            'schroot',
            (['--schroot-name', 'ubuntu-14.04', '--schroot-options', '-p -d /tmp']),
            'schroot -p -d /tmp -c ubuntu-14.04 -- '
        ),
        (
            'schroot',
            (['--schroot-session', 'ubuntu-14.04-session']),
            'schroot -r -c ubuntu-14.04-session -- '
        ),
    ])


@pytest.mark.parametrize(('wrapper_type', 'extra_args', 'contents'), WRAPPER_TYPE_ARGS_CONTENT)
def test_create_automatic_wrappers(wrapper_type, extra_args, contents, tmpdir):
    wrappers_dir = tmpdir.join('wrappers')
    bin_dir = tmpdir.join('bin')
    bin_dir.mkdir()
    _create_executable_file(bin_dir.join('python'))
    _create_executable_file(bin_dir.join('gcc'))

    create_wrappers._main([
                              '-t', wrapper_type,
                              '--bin-dir', str(bin_dir),
                              '--dest-dir', str(wrappers_dir),
                          ] + extra_args)

    _check_wrappers(wrappers_dir, ['run-in', 'python', 'gcc'])

    wrapper = wrappers_dir.join('run-in' + get_wrapper_extension())
    # The wrapped command should be absolute
    wrapper_contents = wrapper.read()
    assert contents in wrapper_contents
    assert '__COMMAND__' not in wrapper_contents


@pytest.mark.parametrize(('wrapper_type', 'extra_args', 'contents'), WRAPPER_TYPE_ARGS_CONTENT)
def test_automatic_wrappers_should_use_absolute_path_by_default(wrapper_type, extra_args, contents, tmpdir):
    wrappers_dir = tmpdir.join('wrappers')
    bin_dir = tmpdir.join('bin')
    bin_dir.mkdir()
    python_bin = _create_executable_file(bin_dir.join('python'))

    create_wrappers._main([
                              '-t', wrapper_type,
                              '--bin-dir', str(bin_dir),
                              '--dest-dir', str(wrappers_dir),
                          ] + extra_args)

    wrapper = wrappers_dir.join('python' + get_wrapper_extension())
    # The wrapped command should be absolute
    assert str(python_bin) in wrapper.read()


@pytest.mark.parametrize(('wrapper_type', 'extra_args', 'contents'), WRAPPER_TYPE_ARGS_CONTENT)
def test_automatic_wrappers_should_use_basename_when_asked(wrapper_type, extra_args, contents, tmpdir):
    wrappers_dir = tmpdir.join('wrappers')
    bin_dir = tmpdir.join('bin')
    bin_dir.mkdir()
    python_bin = _create_executable_file(bin_dir.join('python'))

    create_wrappers._main([
                              '-t', wrapper_type,
                              '--bin-dir', str(bin_dir),
                              '--dest-dir', str(wrappers_dir),
                              '--use-basename',
                          ] + extra_args)

    wrapper = wrappers_dir.join('python' + get_wrapper_extension())
    # The wrapped command should be the basename only
    assert '"{}"'.format(python_bin.basename) in wrapper.read()


@pytest.mark.parametrize(('wrapper_type', 'extra_args', 'contents'), WRAPPER_TYPE_ARGS_CONTENT)
def test_create_only_specified_wrappers(wrapper_type, extra_args, contents, tmpdir):
    wrappers_dir = tmpdir.join('wrappers')

    create_wrappers._main([
                              '-t', wrapper_type,
                              '--files-to-wrap', 'python:gcc',
                              '--dest-dir', str(wrappers_dir),
                          ] + extra_args)

    _check_wrappers(wrappers_dir, ['run-in', 'python', 'gcc'])


@pytest.mark.parametrize(('wrapper_type', 'extra_args', 'contents'), WRAPPER_TYPE_ARGS_CONTENT)
def test_specified_wrappers_should_use_relative_path_by_default(wrapper_type, extra_args, contents, tmpdir):
    wrappers_dir = tmpdir.join('wrappers')

    create_wrappers._main([
                              '-t', wrapper_type,
                              '--files-to-wrap', 'python:gcc',
                              '--dest-dir', str(wrappers_dir),
                          ] + extra_args)

    wrapper = wrappers_dir.join('python' + get_wrapper_extension())
    # The wrapped command should be exactly as we passed to command line
    assert ' "python" ' in wrapper.read()


@pytest.mark.parametrize(('wrapper_type', 'extra_args', 'contents'), WRAPPER_TYPE_ARGS_CONTENT)
def test_specified_wrappers_should_use_absolute_path_when_given_bin_dir(wrapper_type, extra_args, contents, tmpdir):
    wrappers_dir = tmpdir.join('wrappers')
    bin_dir = tmpdir.join('bin')

    create_wrappers._main([
                              '-t', wrapper_type,
                              '--bin-dir', str(bin_dir),
                              '--files-to-wrap', 'python:gcc',
                              '--dest-dir', str(wrappers_dir),
                          ] + extra_args)

    wrapper = wrappers_dir.join('python' + get_wrapper_extension())
    # The wrapped command should be absolute
    assert str(bin_dir.join('python')) in wrapper.read()


@pytest.mark.parametrize(('wrapper_type', 'extra_args', 'contents'), WRAPPER_TYPE_ARGS_CONTENT)
def test_inline_wrappers(wrapper_type, extra_args, contents, tmpdir):
    wrappers_dir = tmpdir.join('wrappers')

    create_wrappers._main([
                              '-t', wrapper_type,
                              '--files-to-wrap', 'python:gcc',
                              '--dest-dir', str(wrappers_dir),
                              '--inline',
                          ] + extra_args)

    # No run-in file
    _check_wrappers(wrappers_dir, ['python', 'gcc'])

    wrapper = wrappers_dir.join('python' + get_wrapper_extension())
    assert contents in wrapper.read()
    wrapper = wrappers_dir.join('gcc' + get_wrapper_extension())
    assert contents in wrapper.read()


@pytest.mark.skipif(sys.platform != 'win32', reason='Extension handling only on Windows')
def test_omit_original_extension(tmpdir):
    wrappers_dir = tmpdir.join('wrappers')
    bin_dir = tmpdir.join('bin')
    create_conda_wrappers([str(bin_dir.join('python.exe')), str(bin_dir.join('gcc.bat'))],
                          str(wrappers_dir),
                          'miniconda/envs/test',
                          inline=False)

    _check_wrappers(wrappers_dir, ['run-in', 'python', 'gcc'])


def test_dont_create_wrapper_when_file_has_same_name(tmpdir):
    wrappers_dir = tmpdir.join('wrappers')
    bin_dir = tmpdir.join('bin')
    os.makedirs(str(bin_dir))
    # It should not create a wrapper for run-in, otherwise it will overwrite
    _create_executable_file(bin_dir.join('run-in'))

    create_conda_wrappers([str(bin_dir.join('python')), str(bin_dir.join('gcc'))],
                          str(wrappers_dir),
                          'miniconda/envs/test',
                          inline=False)

    with open(os.path.join(get_templates_dir(), 'conda', 'run-in' + get_wrapper_extension())) as f:
        expected_run_in_content = f.read() \
                                   .replace('__CONDA_PREFIX__', 'miniconda/envs/test') \
                                   .replace('__CONDA_DEFAULT_ENV__', 'test') \
                                   .replace('__COMMAND__', '')

    assert wrappers_dir.join('run-in' + get_wrapper_extension()).read() == expected_run_in_content


def test_create_custom_wrappers(tmpdir):
    wrappers_dir = tmpdir.join('wrappers')
    run_in_file = _create_custom_run_in_file(tmpdir)

    create_wrappers._main([
                              '-t', 'custom',
                              '--custom-script', str(run_in_file),
                              '--files-to-wrap', 'python',
                              '--dest-dir', str(wrappers_dir),
                          ])

    _check_wrappers(wrappers_dir, ['run-in', 'python'])

    python_wrapper = str(wrappers_dir.join('python' + get_wrapper_extension()))
    python_output = str(subprocess.check_output([python_wrapper, '--version']).decode())
    if sys.platform == 'win32':
        assert python_output.strip('\r\n') == '"python" --version'
    else:
        assert python_output.strip('\r\n') == 'python --version'


@pytest.mark.parametrize(('wrapper_type', 'extra_args', 'contents'), WRAPPER_TYPE_ARGS_CONTENT)
def test_create_wrappers_with_path_spaces(wrapper_type, extra_args, contents, tmpdir):
    wrappers_dir = tmpdir.join('wrappers with space')
    bin_dir = tmpdir.join('bin with space')
    bin_dir.mkdir()
    _create_executable_file(bin_dir.join('python'))

    create_wrappers._main([
                              '-t', wrapper_type,
                              '--bin-dir', str(bin_dir),
                              '--dest-dir', str(wrappers_dir),
                          ] + extra_args)
    wrapper = str(wrappers_dir.join('python' + get_wrapper_extension()))

    subprocess.check_call(wrapper)



def _check_wrappers(wrappers_dir, basenames):
    obtained_wrappers = sorted([f.basename for f in wrappers_dir.listdir()])
    expected_wrappers = sorted([f + get_wrapper_extension() for f in basenames])

    assert obtained_wrappers == expected_wrappers

    for f in wrappers_dir.listdir():
        assert os.access(str(f), os.X_OK)

def _create_custom_run_in_file(tmpdir):
    if sys.platform == 'win32':
        run_in_content = 'echo %*\r\n'
    else:
        run_in_content = '#/bin/sh\necho "$@"\n'

    run_in_filepath = tmpdir.join('custom-run-in' + get_wrapper_extension())
    _create_executable_file(run_in_filepath)

    run_in_filepath.write(run_in_content)

    return run_in_filepath
