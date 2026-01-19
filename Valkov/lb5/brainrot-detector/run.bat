@echo off
echo ========================================
echo   Brainrot Detector - Запуск
echo ========================================
echo.

cd /d "%~dp0"

REM Устанавливаем переменные окружения для кэша на диск H
set HF_HOME=H:\brainrot-detector\models_cache
set HF_DATASETS_CACHE=H:\brainrot-detector\models_cache\datasets
set HF_HUB_CACHE=H:\brainrot-detector\models_cache\hub

REM Создаем директории для кэша
if not exist "models_cache\hub" mkdir "models_cache\hub"
if not exist "models_cache\transformers" mkdir "models_cache\transformers"
if not exist "models_cache\datasets" mkdir "models_cache\datasets"

if not exist "venv\Scripts\activate.bat" (
    echo Создание виртуального окружения...
    python -m venv venv
    if errorlevel 1 (
        echo Ошибка создания виртуального окружения!
        pause
        exit /b 1
    )
)

echo Активация виртуального окружения...
call venv\Scripts\activate.bat

if not exist "venv\lib\site-packages\fastapi" (
    echo Установка зависимостей...
    pip install --only-binary :all: numpy
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Ошибка установки зависимостей!
        pause
        exit /b 1
    )
)

echo.
echo Запуск приложения...
echo.
python run.py

pause

