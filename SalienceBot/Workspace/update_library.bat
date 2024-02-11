@echo off
REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip to the latest version
python -m pip install --upgrade pip

REM Install or upgrade the test library
pip install testlibrary==0.x.x.dev1 --extra-index-url https://test.pypi.org/simple/

REM Run tests
call run_tests.bat

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat
