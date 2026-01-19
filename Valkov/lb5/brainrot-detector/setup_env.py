"""
Скрипт для проверки окружения и установки зависимостей
"""
import sys
import subprocess
import os

def check_ffmpeg():
    """Проверяет наличие ffmpeg"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg установлен")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg не найден")
        print("   Установите FFmpeg: https://ffmpeg.org/download.html")
        return False

def check_python_version():
    """Проверяет версию Python"""
    if sys.version_info < (3, 8):
        print(f"❌ Требуется Python 3.8+, установлен {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]}")
    return True

def check_torch():
    """Проверяет наличие PyTorch"""
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        if torch.cuda.is_available():
            print(f"   CUDA доступна: {torch.cuda.get_device_name(0)}")
        else:
            print("   Используется CPU")
        return True
    except ImportError:
        print("❌ PyTorch не установлен")
        return False

if __name__ == "__main__":
    print("🔍 Проверка окружения...\n")
    
    checks = [
        check_python_version(),
        check_torch(),
        check_ffmpeg()
    ]
    
    print("\n" + "="*50)
    if all(checks):
        print("✅ Все проверки пройдены! Можно запускать приложение.")
    else:
        print("⚠️  Некоторые проверки не пройдены. Установите недостающие компоненты.")

