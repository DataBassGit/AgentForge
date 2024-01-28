@echo off
REM Update the pip library to the latest test build
pip install --upgrade --index-url https://test.pypi.org/simple/ your-library

REM Run tests to verify the new build
python -m unittest discover

REM If this batch file is used by other team members, please ensure that:
REM - You have the necessary permissions to install and upgrade libraries
REM - You have updated the 'your-library' placeholder with the actual library name
REM - The test suite is configured correctly to run with 'unittest discover'
REM - You understand that this will install from the Test PyPI repository, not the main PyPI repository
