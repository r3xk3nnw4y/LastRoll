@echo off
REM Change directory to the folder where the bat file is located
cd /d "%~dp0"

REM Run Django development server
python manage.py runserver

pause
