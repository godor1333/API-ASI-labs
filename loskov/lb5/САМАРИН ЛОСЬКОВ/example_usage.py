"""
Примеры использования проекта
"""

from backend.video_generator import VideoGenerator
from webench2.evaluator import Webench2Evaluator
from webench2.benchmark import run_regression_benchmark, compare_models


def example_generate_video():
    """Пример генерации видео"""
    print("Пример 1: Генерация видео из текста")
    print("-" * 60)
    
    generator = VideoGenerator()
    
    text = "кот-программист бежит по коду, вокруг всплывают окна ошибок"
    video_path = generator.generate_from_text(text, output_filename="example_video.mp4")
    
    print(f"Видео сохранено: {video_path}")


def example_evaluate_video():
    """Пример оценки видео"""
    print("\nПример 2: Оценка видео")
    print("-" * 60)
    
    evaluator = Webench2Evaluator()
    
    # Предполагаем, что видео уже сгенерировано
    video_path = "outputs/videos/example_video.mp4"
    prompt = "кот-программист бежит по коду, вокруг всплывают окна ошибок"
    
    try:
        metrics = evaluator.evaluate_video(video_path, prompt)
        
        print(f"Quality Index: {metrics.get('quality_index', 0):.3f}")
        print(f"CLIP Score (mean): {metrics.get('clip_score', {}).get('mean', 0):.3f}")
        print(f"Image Reward (mean): {metrics.get('image_reward', {}).get('mean', 0):.3f}")
    except FileNotFoundError:
        print(f"Видео не найдено: {video_path}")
        print("Сначала сгенерируйте видео используя example_generate_video()")


def example_full_pipeline():
    """Пример полного пайплайна: генерация + оценка"""
    print("\nПример 3: Полный пайплайн")
    print("-" * 60)
    
    text = "робот рисует картину в космосе, звёзды мерцают на фоне"
    
    # Генерируем
    generator = VideoGenerator()
    video_path = generator.generate_from_text(text)
    
    # Оцениваем
    evaluator = Webench2Evaluator()
    metrics = evaluator.evaluate_video(video_path, text)
    
    print(f"\nРезультаты:")
    print(f"  Видео: {video_path}")
    print(f"  Quality Index: {metrics.get('quality_index', 0):.3f}")
    print(f"  CLIP Score: {metrics.get('clip_score', {}).get('mean', 0):.3f}")


def example_benchmark():
    """Пример запуска регрессионного бенчмарка"""
    print("\nПример 4: Регрессионный бенчмарк")
    print("-" * 60)
    
    print("Запуск бенчмарка на эталонных промптах...")
    results = run_regression_benchmark(model_version="v1.0")
    
    print(f"\nОбработано промптов: {len(results.get('prompts', []))}")
    if 'summary' in results:
        summary = results['summary']
        print(f"Средний Quality Index: {summary.get('quality_index', {}).get('mean', 0):.3f}")
        print(f"Средний CLIP Score: {summary.get('clip_score', {}).get('mean', 0):.3f}")


if __name__ == '__main__':
    print("=" * 60)
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ПРОЕКТА")
    print("=" * 60)
    
    # Раскомментируйте нужный пример
    # example_generate_video()
    # example_evaluate_video()
    # example_full_pipeline()
    # example_benchmark()
    
    print("\n" + "=" * 60)
    print("Раскомментируйте нужный пример в коде для запуска")
    print("=" * 60)
