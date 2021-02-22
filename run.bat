@echo off
:start
echo starting attendance bot!
python main.py
echo attendence bot will start in 10s
timeout /t 10 /nobreak >nul
goto start
pause
