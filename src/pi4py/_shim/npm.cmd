@echo off
set "PYTHON_EXECUTABLE=%PI4PY_PYTHON_EXECUTABLE%"
if not defined PYTHON_EXECUTABLE set "PYTHON_EXECUTABLE=python"
"%PYTHON_EXECUTABLE%" -m pi4py._nodejs npm %*
