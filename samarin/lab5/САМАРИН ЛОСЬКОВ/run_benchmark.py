"""
Скрипт для быстрого запуска регрессионного бенчмарка
"""

import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from webench2.benchmark import run_regression_benchmark

if __name__ == '__main__':
    print("Запуск регрессионного бенчмарка...")
    print("Это может занять много времени в зависимости от количества промптов.")
    
    model_version = input("Введите версию модели (или нажмите Enter для 'default'): ").strip()
    if not model_version:
        model_version = "default"
    
    results = run_regression_benchmark(model_version=model_version)
    
    print("\nБенчмарк завершён!")
    print(f"Обработано промптов: {len(results.get('prompts', []))}")
    
    if 'summary' in results:
        summary = results['summary']
        print("\nСводная статистика:")
        if 'quality_index' in summary:
            print(f"  Средний Quality Index: {summary['quality_index']['mean']:.3f}")
        if 'clip_score' in summary:
            print(f"  Средний CLIP Score: {summary['clip_score']['mean']:.3f}")
