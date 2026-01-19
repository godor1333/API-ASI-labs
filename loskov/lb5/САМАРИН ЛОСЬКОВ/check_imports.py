"""
Проверка всех импортов проекта
"""
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

print("Проверка импортов проекта...")
print("=" * 50)

errors = []

# Проверяем backend
try:
    from backend.video_generator import VideoGenerator
    print("✓ backend.video_generator")
except Exception as e:
    print(f"✗ backend.video_generator: {e}")
    errors.append(f"backend.video_generator: {e}")

try:
    from backend.keyframe_generator import KeyframeGenerator
    print("✓ backend.keyframe_generator")
except Exception as e:
    print(f"✗ backend.keyframe_generator: {e}")
    errors.append(f"backend.keyframe_generator: {e}")

try:
    from backend.comfyui_client import ComfyUIClient
    print("✓ backend.comfyui_client")
except Exception as e:
    print(f"✗ backend.comfyui_client: {e}")
    errors.append(f"backend.comfyui_client: {e}")

# Проверяем webench2
try:
    from webench2.evaluator import Webench2Evaluator
    print("✓ webench2.evaluator")
except Exception as e:
    print(f"✗ webench2.evaluator: {e}")
    errors.append(f"webench2.evaluator: {e}")

try:
    from webench2.metrics import MetricsCalculator
    print("✓ webench2.metrics")
except Exception as e:
    print(f"✗ webench2.metrics: {e}")
    errors.append(f"webench2.metrics: {e}")

try:
    from webench2.benchmark import run_regression_benchmark
    print("✓ webench2.benchmark")
except Exception as e:
    print(f"✗ webench2.benchmark: {e}")
    errors.append(f"webench2.benchmark: {e}")

# Проверяем frontend
try:
    from frontend.app import app
    print("✓ frontend.app")
except Exception as e:
    print(f"✗ frontend.app: {e}")
    errors.append(f"frontend.app: {e}")

print("=" * 50)

if errors:
    print(f"\nНайдено ошибок: {len(errors)}")
    print("\nУстановите недостающие зависимости:")
    print("pip install -r requirements.txt")
    sys.exit(1)
else:
    print("\n✓ Все импорты успешны! Проект готов к запуску.")
    sys.exit(0)
