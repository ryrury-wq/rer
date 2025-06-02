@echo off
set FLASK_APP=app.py
py -m flask run --host=0.0.0.0
pause