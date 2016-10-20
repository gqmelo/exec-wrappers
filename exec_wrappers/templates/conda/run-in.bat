@echo off

@REM This script was based on the original conda activate.bat

@setlocal

@set "CONDA_PREFIX=__CONDA_PREFIX__"
@set "CONDA_DEFAULT_ENV=__CONDA_DEFAULT_ENV__"
@set "CONDA_ENV_PATH=%CONDA_PREFIX%"
@set "CONDA_PATH_BACKUP=%PATH%"
@set "PATH=%CONDA_PREFIX%;%CONDA_PREFIX%\Scripts;%CONDA_PREFIX%\Library\bin;%PATH%"

@REM Run any activate scripts
@if exist "%CONDA_PREFIX%\etc\conda\activate.d" (
    @pushd "%CONDA_PREFIX%\etc\conda\activate.d"
    @for %%g in (*.bat) do @call "%%g"
    @popd
)

@REM Execute the given command
__COMMAND__%*

@endlocal
