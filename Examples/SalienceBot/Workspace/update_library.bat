@echo off
call venv\Scripts\activate.bat
pip install --upgrade mylibrary
pip list
pytest tests
