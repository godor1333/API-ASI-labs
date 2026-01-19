@echo off
echo Активация виртуального окружения...
cd /d "%~dp0"

REM Устанавливаем переменные окружения для кэша на диск H
set HF_HOME=H:\brainrot-detector\models_cache
set HF_DATASETS_CACHE=H:\brainrot-detector\models_cache\datasets
set HF_HUB_CACHE=H:\brainrot-detector\models_cache\hub

REM Создаем директории для кэша
if not exist "models_cache\hub" mkdir "models_cache\hub"
if not exist "models_cache\transformers" mkdir "models_cache\transformers"
if not exist "models_cache\datasets" mkdir "models_cache\datasets"

call venv\Scripts\activate.bat
echo.
echo Виртуальное окружение активировано!
echo Все пакеты установлены на диск H: в папке venv
echo Кэш моделей будет на диске H: в папке models_cache
echo.
echo Для запуска приложения используйте:
echo   python run.py
echo.
cmd /k

