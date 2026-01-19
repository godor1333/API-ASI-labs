"""
Тестовый скрипт для проверки запуска проекта
"""
import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print(f"Текущая директория: {current_dir}")
print(f"Python path: {sys.path[:3]}")

# Проверяем импорты
try:
    print("\nПроверка импортов...")
    from frontend.app import app
    print("✓ frontend.app импортирован успешно")
    
    print("\nЗапуск веб-интерфейса...")
    print("Откройте браузер и перейдите на http://localhost:5000")
    print("Для остановки нажмите Ctrl+C\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
    
except ImportError as e:
    print(f"✗ Ошибка импорта: {e}")
    print("\nПопробуйте установить зависимости:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"✗ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
