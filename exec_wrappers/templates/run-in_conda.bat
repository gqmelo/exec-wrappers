@echo off

@set "CONDA_DEFAULT_ENV=@CONDA_ENV_DIR@"

@endlocal & (
    @set PATH="%CONDA_DEFAULT_ENV%";"%CONDA_DEFAULT_ENV%\Scripts";"%CONDA_DEFAULT_ENV%\Library\bin";%PATH%

    @REM Run any activate scripts
    @if exist "%CONDA_DEFAULT_ENV%\etc\conda\activate.d" (
        @pushd "%CONDA_DEFAULT_ENV%\etc\conda\activate.d"
        @for %%g in (*.bat) do @call "%%g"
        @popd
    )
)

%*