@echo off
:: ============================================================
::  Security Monitor – Task Scheduler Launcher
::  Place this .bat file in the SAME folder as monitor.py
:: ============================================================

:: Change to the script's own directory so all relative paths work
cd /d "%~dp0"

:: Use the Python executable that has the required packages installed.
:: If "python" isn't on PATH, replace with the full path, e.g.:
::   C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe
set PYTHON=python

:: Run the monitor (pythonw.exe hides the console window completely)
:: Switch to "python" if you want a visible console for debugging.
set PYTHONW=pythonw

%PYTHONW% monitor.py >> "%~dp0monitor_launcher.log" 2>&1
