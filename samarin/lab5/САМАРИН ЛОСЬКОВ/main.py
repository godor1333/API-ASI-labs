"""
Главный скрипт для запуска генерации видео и оценки
"""

import argparse
import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from backend.video_generator import VideoGenerator
from webench2.evaluator import Webench2Evaluator
from webench2.benchmark import run_regression_benchmark, compare_models


def generate_and_evaluate(text: str, output_name: str = None):
    """
    Генерация видео и его оценка
    
    Args:
        text: Текстовое описание
        output_name: Имя выходного файла
    """
    print("=" * 60)
    print("ГЕНЕРАЦИЯ И ОЦЕНКА ВИДЕО")
    print("=" * 60)
    
    # Генерируем видео
    generator = VideoGenerator()
    video_path = generator.generate_from_text(text, output_filename=output_name)
    
    print(f"\nВидео сгенерировано: {video_path}")
    
    # Оцениваем видео
    evaluator = Webench2Evaluator()
    metrics = evaluator.evaluate_video(video_path, text)
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ОЦЕНКИ")
    print("=" * 60)
    print(f"Quality Index: {metrics.get('quality_index', 0):.3f}")
    
    if "clip_score" in metrics:
        print(f"CLIP Score (mean): {metrics['clip_score']['mean']:.3f}")
        print(f"CLIP Score (min): {metrics['clip_score']['min']:.3f}")
        print(f"CLIP Score (std): {metrics['clip_score']['std']:.3f}")
    
    if "image_reward" in metrics:
        print(f"Image Reward (mean): {metrics['image_reward']['mean']:.3f}")
    
    if "static_frames" in metrics:
        print(f"Статичные кадры: {metrics['static_frames']['count']} ({metrics['static_frames']['ratio']*100:.1f}%)")
    
    if "dark_frames" in metrics:
        print(f"Тёмные кадры: {metrics['dark_frames']['count']} ({metrics['dark_frames']['ratio']*100:.1f}%)")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Генерация видео и оценка через Webench2")
    
    subparsers = parser.add_subparsers(dest='command', help='Команды')
    
    # Команда генерации
    gen_parser = subparsers.add_parser('generate', help='Генерация видео из текста')
    gen_parser.add_argument('text', type=str, help='Текстовое описание')
    gen_parser.add_argument('--output', type=str, help='Имя выходного файла')
    
    # Команда оценки
    eval_parser = subparsers.add_parser('evaluate', help='Оценка существующего видео')
    eval_parser.add_argument('video', type=str, help='Путь к видео')
    eval_parser.add_argument('prompt', type=str, help='Текстовое описание')
    
    # Команда генерации и оценки
    full_parser = subparsers.add_parser('full', help='Генерация и оценка')
    full_parser.add_argument('text', type=str, help='Текстовое описание')
    full_parser.add_argument('--output', type=str, help='Имя выходного файла')
    
    # Команда бенчмарка
    bench_parser = subparsers.add_parser('benchmark', help='Запуск регрессионного бенчмарка')
    bench_parser.add_argument('--prompts', type=str, help='Путь к файлу промптов')
    bench_parser.add_argument('--version', type=str, help='Версия модели')
    
    # Команда сравнения
    comp_parser = subparsers.add_parser('compare', help='Сравнение двух моделей')
    comp_parser.add_argument('run_a', type=str, help='Файл результатов модели A')
    comp_parser.add_argument('run_b', type=str, help='Файл результатов модели B')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        generator = VideoGenerator()
        video_path = generator.generate_from_text(args.text, output_filename=args.output)
        print(f"Видео сгенерировано: {video_path}")
    
    elif args.command == 'evaluate':
        evaluator = Webench2Evaluator()
        metrics = evaluator.evaluate_video(args.video, args.prompt)
        print(f"Quality Index: {metrics.get('quality_index', 0):.3f}")
    
    elif args.command == 'full':
        generate_and_evaluate(args.text, args.output)
    
    elif args.command == 'benchmark':
        run_regression_benchmark(
            prompts_file=args.prompts,
            model_version=args.version
        )
    
    elif args.command == 'compare':
        import json
        with open(args.run_a, 'r', encoding='utf-8') as f:
            results_a = json.load(f)
        with open(args.run_b, 'r', encoding='utf-8') as f:
            results_b = json.load(f)
        
        comparison = compare_models(results_a, results_b)
        print(f"Сравнение завершено. Результаты сохранены.")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
