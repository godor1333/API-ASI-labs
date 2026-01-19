@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Запуск веб-интерфейса...
echo Откройте браузер и перейдите на http://localhost:5000
python run_web.py
pause
