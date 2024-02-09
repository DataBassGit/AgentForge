@echo off
REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade the library in the virtual environment
pip install --upgrade --extra-index-url https://test.pypi.org/simple/ your-library

REM Run tests
python -m unittest discover -s tests

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat
