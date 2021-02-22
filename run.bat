@echo off
:start
echo starting attendence bot!
python main.py
echo attendence bot will start in 10s
timeout /t 10 /nobreak >nul
goto start
pause