@echo off

cd %~d0%~p0

set pathvar=%~d0%~p0

pythonw "%pathvar%idl2py.py" %1
