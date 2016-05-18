@echo off

@REM This script was based on the original conda activate.bat

@setlocal

@set "CONDA_DEFAULT_ENV=__CONDA_ENV_DIR__"
@set PATH="%CONDA_DEFAULT_ENV%";"%CONDA_DEFAULT_ENV%\Scripts";"%CONDA_DEFAULT_ENV%\Library\bin";%PATH%

@REM Run any activate scripts
@if exist "%CONDA_DEFAULT_ENV%\etc\conda\activate.d" (
    @pushd "%CONDA_DEFAULT_ENV%\etc\conda\activate.d"
    @for %%g in (*.bat) do @call "%%g"
    @popd
)

@REM Execute the given command
%*

@endlocal
