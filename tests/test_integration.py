import os
import stat
import subprocess
import sys
import textwrap

import pytest

from exec_wrappers import create_wrappers
from exec_wrappers.create_wrappers import get_wrapper_extension

try:
    from shutil import which
except ImportError:
    from backports.shutil_which import which


def test_execute_virtualenv_wrappers(tmpdir, monkeypatch):
    import virtualenv

    # monkey patch the current dir to make sure we convert the relative paths
    # passed as arguments to absolute
    monkeypatch.chdir(tmpdir)
    virtualenv.create_environment(
        "virtual envs/test", no_setuptools=True, no_pip=True, no_wheel=True
    )

    if sys.platform != "win32":
        bin_dir = "virtual envs/test/bin"
    else:
        bin_dir = "virtual envs/test/Scripts"

    create_wrappers._main(
        [
            "-t",
            "virtualenv",
            "--virtual-env-dir",
            "virtual envs/test",
            "--bin-dir",
            bin_dir,
            "--dest-dir",
            "wrappers",
        ]
    )

    environ_from_activate = _environ_from_activate(
        _activate_virtualenv_script(), tmpdir
    )
    # Remove some variables we don't care
    if sys.platform != "win32":
        environ_from_activate.pop("PS1", None)
        environ_from_activate.pop("SHLVL")
    else:
        environ_from_activate.pop("_OLD_VIRTUAL_PATH")
        environ_from_activate.pop("_OLD_VIRTUAL_PROMPT")
        environ_from_activate.pop("PROMPT")
        environ_from_activate["PATH"] = os.path.normcase(environ_from_activate["PATH"])
        environ_from_activate["VIRTUAL_ENV"] = os.path.normcase(
            environ_from_activate["VIRTUAL_ENV"]
        )

    environ_from_wrapper = _environ_from_wrapper()
    if sys.platform != "win32":
        environ_from_wrapper.pop("SHLVL")
    else:
        environ_from_wrapper.pop("PROMPT")
        environ_from_wrapper["PATH"] = os.path.normcase(environ_from_wrapper["PATH"])
        environ_from_wrapper["VIRTUAL_ENV"] = os.path.normcase(
            environ_from_wrapper["VIRTUAL_ENV"]
        )

    assert environ_from_activate == environ_from_wrapper


def test_execute_conda_wrappers(tmpdir, monkeypatch):
    # monkey patch the current dir to make sure we convert the relative paths
    # passed as arguments to absolute
    monkeypatch.chdir(tmpdir)
    if not which("conda"):
        pytest.fail(
            "This test needs conda. Make sure you have miniconda "
            "installed and added to PATH env var"
        )
    subprocess.check_call(
        ["conda", "create", "--clone", "root", "-p", "conda envs/test"]
    )

    activate_scripts_path = tmpdir.join("conda envs/test/etc/conda/activate.d")

    if sys.platform != "win32":
        bin_dir = "conda envs/test/bin"
        # Create a custom activate script to ensure that the wrapper runs it.
        activate_scripts_path.join("custom_activate.sh").write(
            textwrap.dedent(
                """
                export ENV_VAR_FROM_ACTIVATE='SOME_VALUE'
                """
            ),
            ensure=True,
        )
    else:
        bin_dir = "conda envs/test"
        # Create a custom activate script to ensure that the wrapper runs it.
        activate_scripts_path.join("custom_activate.bat").write(
            textwrap.dedent(
                """
                @set "ENV_VAR_FROM_ACTIVATE=SOME_VALUE"
                """
            ),
            ensure=True,
        )

    create_wrappers._main(
        [
            "-t",
            "conda",
            "--conda-env-dir",
            "conda envs/test",
            "--bin-dir",
            bin_dir,
            "--dest-dir",
            "wrappers",
        ]
    )

    environ_from_activate = _environ_from_activate(_activate_conda_script(), tmpdir)
    environ_from_wrapper = _environ_from_wrapper()
    assert environ_from_wrapper["CONDA_DEFAULT_ENV"] == "test"
    assert environ_from_wrapper["CONDA_ENV_PATH"] == str(tmpdir.join("conda envs/test"))
    assert environ_from_wrapper["ENV_VAR_FROM_ACTIVATE"] == "SOME_VALUE"

    if sys.platform != "win32":
        # conda 4.6 began to add a path like <conda_root_dir>/condabin, but
        # we have no easy way to find out the root dir from the wrapper script.
        # So let's just filter it for now.
        path = environ_from_activate["PATH"].split(":")
        filtered_path = [p for p in path if "/condabin" not in p]
        environ_from_activate["PATH"] = ":".join(filtered_path)

        path = environ_from_wrapper["PATH"].split(":")
        filtered_path = [p for p in path if "/condabin" not in p]
        environ_from_wrapper["PATH"] = ":".join(filtered_path)

    # Remove some variables we don't care about
    variables_to_ignore = [
        # It's an absolute path when activating but just the env name when
        # using the wrapper
        "CONDA_DEFAULT_ENV",
        # Only present on old conda versions
        "CONDA_ENV_PATH",
        # Only present on recent conda versions (>=4.4)
        "CONDA_PROMPT_MODIFIER",
        "CONDA_SHLVL",
        "CONDA_PYTHON_EXE",
        # Not present on conda >=4.4
        "CONDA_PATH_BACKUP",
        "CONDA_PS1_BACKUP",
        # Only present on conda >=4.5
        "CONDA_EXE",
        # Only present on conda >=4.6.9
        # Those variables seem to be used for dev mode only
        # https://github.com/conda/conda/pull/8435/commits/9a4589a1fabc66c122fb0c20fa1f3aa2c8b1758b
        "_CE_CONDA",
        "_CE_M",
    ]

    if sys.platform != "win32":
        variables_to_ignore.extend(["PS1", "SHLVL"])
    else:
        variables_to_ignore.extend(
            [
                "CONDA_ROOT",
                "PROMPT",
                # Only present on conda >=4.5
                "PYTHONIOENCODING",
            ]
        )

    for variable_name in variables_to_ignore:
        environ_from_activate.pop(variable_name, None)
        environ_from_wrapper.pop(variable_name, None)

    assert environ_from_activate == environ_from_wrapper


def _activate_virtualenv_script():
    if sys.platform == "win32":
        return """@echo off
            call "virtual envs\\test\\Scripts\\activate.bat"
        """
    else:
        return """#!/usr/bin/env bash
            source 'virtual envs/test/bin/activate'
        """


def _activate_conda_script():
    if sys.platform == "win32":
        return """@echo off
            @for /F %%i in ('conda info --root') do @set "CONDA_ROOT=%%i"
            call "%CONDA_ROOT%\\Scripts\\activate.bat" "conda envs\\test"
        """
    else:
        return """#!/usr/bin/env bash
            source "$(conda info --root)/bin/activate" "conda envs/test"
        """


def _environ_from_wrapper():
    python_wrapper = os.path.normpath("wrappers/python") + get_wrapper_extension()
    with pytest.raises(subprocess.CalledProcessError) as exc_info:
        # Return a non-zero exit code on purpose, to make sure wrapper returns it.
        subprocess.check_output(
            [
                python_wrapper,
                "-c",
                "from os import environ; print(dict(environ))"
                "; import sys; sys.exit(42)",
            ]
        )
    assert exc_info.value.returncode == 42
    output = exc_info.value.output
    environ_from_wrapper = eval(output)
    return environ_from_wrapper


def _environ_from_activate(activate_script, tmpdir):
    activate_file = tmpdir.join("environ-from-activate") + get_wrapper_extension()
    activate_file.write(
        """%s
        python -c "from os import environ; print(dict(environ))"
    """
        % activate_script
    )
    activate_file.chmod(activate_file.stat().mode | stat.S_IXUSR)
    output = subprocess.check_output(str(activate_file))
    environ_from_activate = eval(output)
    return environ_from_activate
