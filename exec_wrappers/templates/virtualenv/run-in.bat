@echo off

@setlocal

@for %%i in ("__VIRTUAL_ENV__") do @set "VIRTUAL_ENV=%%~si"
@set PYTHONHOME=
@set "PATH=%VIRTUAL_ENV%\Scripts;%PATH%"

@rem Execute the given command
__COMMAND__%*

@endlocal
