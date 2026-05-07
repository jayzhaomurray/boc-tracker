@echo off
cd /d "%~dp0"
git add -A
git commit -m "Update dashboard %date% %time%"
git push
pause
