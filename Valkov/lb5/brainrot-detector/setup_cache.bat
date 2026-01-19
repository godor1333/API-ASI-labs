@echo off
echo ========================================
echo   Настройка кэша Hugging Face на диск H:
echo ========================================
echo.

cd /d "%~dp0"

setx HF_HOME "H:\brainrot-detector\models_cache"
setx HF_DATASETS_CACHE "H:\brainrot-detector\models_cache\datasets"
setx HF_HUB_CACHE "H:\brainrot-detector\models_cache\hub"

echo.
echo Переменные окружения установлены!
echo.
echo Для применения изменений:
echo 1. Закройте и откройте заново командную строку
echo 2. Или перезагрузите компьютер
echo.
echo Кэш будет сохраняться в: H:\brainrot-detector\models_cache
echo.
pause



