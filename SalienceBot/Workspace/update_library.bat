@echo off
REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip to ensure we're using the latest version
python -m pip install --upgrade pip

REM Install or upgrade the library in test mode
pip install --upgrade --force-reinstall <library_name>==<test_version>

REM Run tests
call run_tests.bat

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat
