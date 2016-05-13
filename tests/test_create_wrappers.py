import os
import pytest

import stat

from exec_wrappers.create_wrappers import list_executable_files, create_conda_wrappers, \
    create_schroot_wrappers, get_templates_dir


def test_list_executable_files(tmpdir):
    executable_owner = _create_file(tmpdir.join('executable_owner'), stat.S_IXUSR)

    _create_file(tmpdir.join('non_executable'), stat.S_IRUSR)

    assert list_executable_files(str(tmpdir)) == [str(executable_owner)]


def test_list_executable_files_sorted(tmpdir):
    filename_1 = _create_file(tmpdir.join('1_executable'), stat.S_IXUSR)
    filename_2 = _create_file(tmpdir.join('j_executable'), stat.S_IXUSR)
    filename_3 = _create_file(tmpdir.join('z_executable'), stat.S_IXUSR)

    assert list_executable_files(str(tmpdir)) == [
        str(filename_1),
        str(filename_2),
        str(filename_3)
    ]


def _create_file(filepath, mode):
    filepath.write('')
    filepath.chmod(filepath.stat().mode | mode)

    return filepath


def test_create_conda_wrappers(tmpdir):
    wrappers_dir = tmpdir.join('wrappers')
    bin_dir = tmpdir.join('bin')
    create_conda_wrappers([str(bin_dir.join('python')), str(bin_dir.join('gcc'))],
                          '/home/saddan/miniconda/envs/test',
                          str(wrappers_dir))

    assert wrappers_dir.join('run-in').exists()
    assert os.access(str(wrappers_dir.join('run-in')), os.X_OK)
    assert wrappers_dir.join('python').exists()
    assert os.access(str(wrappers_dir.join('python')), os.X_OK)
    assert wrappers_dir.join('gcc').exists()
    assert os.access(str(wrappers_dir.join('gcc')), os.X_OK)


def test_create_schroot_wrappers(tmpdir):
    wrappers_dir = tmpdir.join('wrappers')
    bin_dir = tmpdir.join('bin')
    create_schroot_wrappers([str(bin_dir.join('python')), str(bin_dir.join('gcc'))],
                          'ubuntu-14.04',
                          str(wrappers_dir))

    assert wrappers_dir.join('run-in').exists()
    assert os.access(str(wrappers_dir.join('run-in')), os.X_OK)
    assert wrappers_dir.join('python').exists()
    assert os.access(str(wrappers_dir.join('python')), os.X_OK)
    assert wrappers_dir.join('gcc').exists()
    assert os.access(str(wrappers_dir.join('gcc')), os.X_OK)


def test_dont_create_wrapper_when_file_has_same_name(tmpdir):
    wrappers_dir = tmpdir.join('wrappers')
    bin_dir = tmpdir.join('bin')
    os.makedirs(str(bin_dir))
    # It should not create a wrapper for run_in, otherwise it will overwrite
    _create_file(bin_dir.join('run-in'), stat.S_IXUSR)

    create_schroot_wrappers([str(bin_dir.join('run-in'))],
                          'ubuntu-14.04',
                          str(wrappers_dir))

    with open(os.path.join(get_templates_dir(), 'run-in_schroot')) as f:
        expected_run_in_content = f.read().replace('@CHROOT@', 'ubuntu-14.04')

    assert wrappers_dir.join('run-in').read() == expected_run_in_content

