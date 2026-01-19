@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo Запуск проекта Webench2
echo ========================================
echo.

REM Проверка зависимостей
echo Проверка зависимостей...
python check_imports.py >nul 2>&1
if errorlevel 1 (
    echo.
    echo Обнаружены отсутствующие зависимости!
    echo Установка зависимостей из requirements.txt...
    pip install -r requirements.txt
    echo.
    echo Проверка импортов снова...
    python check_imports.py
    if errorlevel 1 (
        echo.
        echo Ошибка: не все зависимости установлены
        pause
        exit /b 1
    )
)

echo.
echo Выберите режим:
echo 1. Веб-интерфейс
echo 2. Генерация и оценка видео
echo 3. Регрессионный бенчмарк
echo 4. Проверка импортов
echo.
set /p choice="Введите номер (1-4): "

if "%choice%"=="1" (
    echo.
    echo Запуск веб-интерфейса...
    echo Откройте браузер и перейдите на http://localhost:5000
    echo.
    python run_web.py
) else if "%choice%"=="2" (
    echo.
    set /p text="Введите текстовое описание: "
    echo.
    python main.py full "%text%"
) else if "%choice%"=="3" (
    echo.
    echo Запуск регрессионного бенчмарка...
    echo.
    python run_benchmark.py
) else if "%choice%"=="4" (
    echo.
    python check_imports.py
) else (
    echo Неверный выбор
)

pause
