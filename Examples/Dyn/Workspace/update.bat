@echo off

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Upgrade library
pip install --upgrade mylibrary

REM Run tests
python -m unittest
