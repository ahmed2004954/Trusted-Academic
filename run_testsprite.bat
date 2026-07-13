@echo off
REM run_testsprite.bat
REM Run the PowerShell wrapper to execute TestSprite CLI.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_testsprite.ps1"
pause
