@echo off

call venv\Scripts\activate
pip install --upgrade testpackage
python -m unittest discover tests
