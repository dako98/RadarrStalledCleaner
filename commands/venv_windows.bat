@echo off

set PYTHON=python

powershell -NoProfile -ExecutionPolicy Bypass -Command "Write-Host '--------Building venv--------' -ForegroundColor Cyan"
%PYTHON% -m venv .venv
call .venv\Scripts\activate.bat

powershell -NoProfile -ExecutionPolicy Bypass -Command "Write-Host '--------Upgrading pip--------' -ForegroundColor Cyan"
%PYTHON% -m pip install pip setuptools --upgrade
pip install -e .

call .venv\Scripts\deactivate.bat
powershell -NoProfile -ExecutionPolicy Bypass -Command "Write-Host '--------Finished building venv--------' -ForegroundColor Cyan"
