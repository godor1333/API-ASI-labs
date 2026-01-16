@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist "maze.json" (
    echo Ошибка: файл maze.json не найден!
    echo Создаю файл maze.json...
    python generate_maze.py
)
python main.py
if errorlevel 1 pause
