"""
Скрипт для запуска веб-интерфейса
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from frontend.app import app

if __name__ == '__main__':
    print("Запуск веб-интерфейса...")
    print("Откройте браузер и перейдите на http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
