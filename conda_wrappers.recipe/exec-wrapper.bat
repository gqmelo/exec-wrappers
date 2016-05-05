@echo off

@set "CONDA_ENV_PATH=%~dp0\.."

@endlocal & (
    @SET PATH="%CONDA_ENV_PATH%";"%CONDA_ENV_PATH%\Scripts";"%CONDA_ENV_PATH%\Library\bin";%PATH%

    @REM Run any activate scripts
    @IF EXIST "%CONDA_ENV_PATH%\etc\conda\activate.d" (
        @PUSHD "%CONDA_ENV_PATH%\etc\conda\activate.d"
        @FOR %%g in (*.bat) DO @CALL "%%g"
        @POPD
    )
)

%*