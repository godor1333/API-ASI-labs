@echo off
echo ========================================
echo   Установка зависимостей
echo   Все файлы будут на диске H:
echo ========================================
echo.

cd /d "%~dp0"

if not exist "venv" (
    echo Создание виртуального окружения на диске H:...
    python -m venv venv
    if errorlevel 1 (
        echo Ошибка создания виртуального окружения!
        pause
        exit /b 1
    )
)

echo Активация виртуального окружения...
call venv\Scripts\activate.bat

echo.
echo Установка numpy (только бинарные пакеты)...
pip install --only-binary :all: numpy>=2.0.0
if errorlevel 1 (
    echo Ошибка установки numpy. Попробуйте: pip install numpy
    pause
    exit /b 1
)

echo.
echo Установка остальных зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
    echo Ошибка установки зависимостей.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Установка завершена успешно!
echo Все пакеты находятся в: H:\brainrot-detector\venv
echo ========================================
pause

