#!/usr/bin/env python3
"""
Скрипт для запуска приложения без auto-reload
Используйте этот скрипт, если постоянные перезагрузки мешают работе
"""
import sys
import os
from pathlib import Path

# Проверяем, что мы в виртуальном окружении
if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    venv_path = Path(__file__).parent / "venv"
    if venv_path.exists():
        print("⚠️  Виртуальное окружение не активировано!")
        print(f"Активируйте его командой:")
        print(f"  {venv_path / 'Scripts' / 'Activate.ps1'}")
        print("\nИли используйте run.bat для автоматического запуска")
        sys.exit(1)

import uvicorn
from config import HOST, PORT

if __name__ == "__main__":
    print(f"🚀 Запуск Brainrot Detector на http://{HOST}:{PORT}")
    print("📊 Откройте браузер и перейдите по адресу выше")
    print(f"📁 Виртуальное окружение: {sys.prefix}")
    print("⚠️  Запуск БЕЗ auto-reload (изменения в коде не применяются автоматически)")
    print("   Для разработки используйте run.py")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=False)


