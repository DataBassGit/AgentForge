@echo off
REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip to the latest version
python -m pip install --upgrade pip

REM Install or upgrade the test build of the library
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple your-library-name --pre

REM Run tests
call run_tests.bat

REM Deactivate the virtual environment
call venv\Scripts\deactivate.bat
