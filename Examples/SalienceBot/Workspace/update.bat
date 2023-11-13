@echo off

REM Activate virtual environment
call .\env\Scripts\activate.bat

REM Upgrade package
pip install --upgrade mypackage

REM Run tests
pytest

REM Deactivate virtual environment
call .\env\Scripts\deactivate.bat