@echo off

@setlocal

@set "VIRTUAL_ENV=__VIRTUAL_ENV__"
@set PYTHONHOME=
@set "PATH=%VIRTUAL_ENV%\Scripts;%PATH%"

@rem Execute the given command
%*

@endlocal
