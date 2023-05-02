@echo off

set PYTHON=python
set VENV=.venv
set PACKAGE_NAME=stalled-cleaner

call %VENV%\Scripts\activate.bat
%PYTHON% -m %PACKAGE_NAME%.main
call %VENV%\Scripts\deactivate.bat
