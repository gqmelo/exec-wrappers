
@if "%CONDA_DEFAULT_ENV%" == "" (
    @for /F %%i in ('conda info --root') do set "ENV_DIR=%%i"
    @echo
    @echo CONDA_DEFAULT_ENV is not set. Assuming conda root env
) else (
    @set "ENV_DIR=%CONDA_DEFAULT_ENV%"
)

@set "BIN_DIR=%ENV_DIR%\Library\bin"
@set "SCRIPTS_DIR=%ENV_DIR%\Scripts"
@set "WRAPPERS_DIR=%ENV_DIR%\Scripts\wrappers\conda"

@echo Creating wrappers from %BIN_DIR% to %WRAPPERS_DIR%
@create-wrappers ^
    -t conda ^
    -b %BIN_DIR% ^
    -d %WRAPPERS_DIR% ^
    --conda-env-dir %ENV_DIR%

@echo Creating wrappers from %SCRIPTS_DIR% to %WRAPPERS_DIR%
@create-wrappers ^
    -t conda ^
    -b %SCRIPTS_DIR% ^
    -d %WRAPPERS_DIR% ^
    --conda-env-dir %ENV_DIR%

@echo Creating wrappers from %ENV_DIR% to %WRAPPERS_DIR%
@create-wrappers ^
    -t conda ^
    -b %ENV_DIR% ^
    -d %WRAPPERS_DIR% ^
    --conda-env-dir %ENV_DIR%
