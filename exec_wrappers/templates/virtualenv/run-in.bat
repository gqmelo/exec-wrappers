@echo off

@setlocal

@for %%i in ("__VIRTUAL_ENV__") do @set "VIRTUAL_ENV=%%~si"
@set PYTHONHOME=
@set "PATH=%VIRTUAL_ENV%\Scripts;%PATH%"

@rem Execute the given command
@rem Nothing must be present after that line (not even a @rem), see issue #30
__COMMAND__%*
