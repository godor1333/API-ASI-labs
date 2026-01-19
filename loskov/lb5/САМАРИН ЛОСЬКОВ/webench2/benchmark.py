"""
Модуль для регрессионного бенчмарка и A/B сравнения моделей
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd
from datetime import datetime

from .evaluator import Webench2Evaluator
from backend.video_generator import VideoGenerator


def load_benchmark_prompts(prompts_file: str) -> List[Dict[str, str]]:
    """
    Загрузка эталонных промптов для бенчмарка
    
    Args:
        prompts_file: Путь к файлу с промптами
        
    Returns:
        List[Dict[str, str]]: Список промптов с метаданными
    """
    try:
        with open(prompts_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "prompts" in data:
                return data["prompts"]
            else:
                raise ValueError("Неверный формат файла промптов")
    except FileNotFoundError:
        print(f"Файл промптов не найден: {prompts_file}")
        return []
    except Exception as e:
        print(f"Ошибка загрузки промптов: {e}")
        return []


def run_regression_benchmark(
    prompts_file: Optional[str] = None,
    output_dir: Optional[str] = None,
    model_version: Optional[str] = None
) -> Dict[str, Any]:
    """
    Запуск регрессионного бенчмарка на наборе фиксированных промптов
    
    Args:
        prompts_file: Путь к файлу с промптами
        output_dir: Директория для сохранения результатов
        model_version: Версия модели (для идентификации)
        
    Returns:
        dict: Результаты бенчмарка
    """
    if prompts_file is None:
        prompts_file = os.path.join(os.path.dirname(__file__), "..", "prompts", "benchmark_prompts.json")
    
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "benchmark")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Загружаем промпты
    prompts = load_benchmark_prompts(prompts_file)
    
    if not prompts:
        print("Промпты не найдены, используем тестовые")
        prompts = [
            {"id": "test_1", "text": "кот-программист бежит по коду, вокруг всплывают окна ошибок"},
            {"id": "test_2", "text": "робот рисует картину в космосе"},
            {"id": "test_3", "text": "дерево растёт в пустыне, вокруг появляются цветы"}
        ]
    
    print(f"Запуск регрессионного бенчмарка на {len(prompts)} промптах")
    
    # Инициализируем генератор и оценщик
    generator = VideoGenerator()
    evaluator = Webench2Evaluator()
    
    results = {
        "model_version": model_version or "unknown",
        "timestamp": datetime.now().isoformat(),
        "prompts": [],
        "summary": {}
    }
    
    all_metrics = []
    
    for i, prompt_data in enumerate(prompts):
        prompt_id = prompt_data.get("id", f"prompt_{i}")
        prompt_text = prompt_data.get("text", "")
        category = prompt_data.get("category", "general")
        
        print(f"\n[{i+1}/{len(prompts)}] Обработка промпта: {prompt_id}")
        print(f"  Текст: {prompt_text[:60]}...")
        
        try:
            # Генерируем видео
            video_path = generator.generate_from_text(prompt_text)
            
            # Оцениваем видео
            metrics = evaluator.evaluate_video(video_path, prompt_text, save_results=False)
            
            # Сохраняем результаты
            result_entry = {
                "prompt_id": prompt_id,
                "prompt_text": prompt_text,
                "category": category,
                "video_path": video_path,
                "metrics": metrics
            }
            results["prompts"].append(result_entry)
            all_metrics.append(metrics)
            
        except Exception as e:
            print(f"  Ошибка при обработке промпта {prompt_id}: {e}")
            results["prompts"].append({
                "prompt_id": prompt_id,
                "prompt_text": prompt_text,
                "category": category,
                "error": str(e)
            })
    
    # Вычисляем сводную статистику
    if all_metrics:
        results["summary"] = calculate_summary_statistics(all_metrics)
    
    # Сохраняем результаты
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(output_dir, f"benchmark_{timestamp_str}.json")
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nБенчмарк завершён. Результаты сохранены: {results_file}")
    
    return results


def calculate_summary_statistics(metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Вычисление сводной статистики по всем метрикам
    
    Args:
        metrics_list: Список словарей с метриками
        
    Returns:
        dict: Сводная статистика
    """
    summary = {}
    
    # CLIPScore статистика
    clip_scores = [m.get("clip_score", {}).get("mean", 0) for m in metrics_list if "clip_score" in m]
    if clip_scores:
        summary["clip_score"] = {
            "mean": float(sum(clip_scores) / len(clip_scores)),
            "min": float(min(clip_scores)),
            "max": float(max(clip_scores)),
            "std": float((sum((x - sum(clip_scores)/len(clip_scores))**2 for x in clip_scores) / len(clip_scores))**0.5)
        }
    
    # ImageReward статистика
    image_rewards = [m.get("image_reward", {}).get("mean", 0) for m in metrics_list if "image_reward" in m]
    if image_rewards:
        summary["image_reward"] = {
            "mean": float(sum(image_rewards) / len(image_rewards)),
            "min": float(min(image_rewards)),
            "max": float(max(image_rewards))
        }
    
    # Quality Index статистика
    quality_indices = [m.get("quality_index", 0) for m in metrics_list if "quality_index" in m]
    if quality_indices:
        summary["quality_index"] = {
            "mean": float(sum(quality_indices) / len(quality_indices)),
            "min": float(min(quality_indices)),
            "max": float(max(quality_indices))
        }
    
    # Проблемы
    static_ratios = [m.get("static_frames", {}).get("ratio", 0) for m in metrics_list if "static_frames" in m]
    if static_ratios:
        summary["static_frames_ratio"] = float(sum(static_ratios) / len(static_ratios))
    
    dark_ratios = [m.get("dark_frames", {}).get("ratio", 0) for m in metrics_list if "dark_frames" in m]
    if dark_ratios:
        summary["dark_frames_ratio"] = float(sum(dark_ratios) / len(dark_ratios))
    
    return summary


def compare_models(
    model_a_results: Dict[str, Any],
    model_b_results: Dict[str, Any],
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    A/B сравнение двух моделей
    
    Args:
        model_a_results: Результаты модели A
        model_b_results: Результаты модели B
        output_dir: Директория для сохранения сравнения
        
    Returns:
        dict: Результаты сравнения
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "results", "comparisons")
    
    os.makedirs(output_dir, exist_ok=True)
    
    comparison = {
        "model_a": model_a_results.get("model_version", "unknown"),
        "model_b": model_b_results.get("model_version", "unknown"),
        "timestamp": datetime.now().isoformat(),
        "comparisons": []
    }
    
    # Создаём словари для быстрого доступа
    results_a = {p["prompt_id"]: p for p in model_a_results.get("prompts", []) if "metrics" in p}
    results_b = {p["prompt_id"]: p for p in model_b_results.get("prompts", []) if "metrics" in p}
    
    # Находим общие промпты
    common_prompts = set(results_a.keys()) & set(results_b.keys())
    
    for prompt_id in common_prompts:
        metrics_a = results_a[prompt_id]["metrics"]
        metrics_b = results_b[prompt_id]["metrics"]
        
        comparison_entry = {
            "prompt_id": prompt_id,
            "prompt_text": results_a[prompt_id]["prompt_text"],
            "deltas": {}
        }
        
        # Вычисляем дельты для метрик
        if "clip_score" in metrics_a and "clip_score" in metrics_b:
            delta_clip = metrics_b["clip_score"]["mean"] - metrics_a["clip_score"]["mean"]
            comparison_entry["deltas"]["clip_score"] = float(delta_clip)
        
        if "image_reward" in metrics_a and "image_reward" in metrics_b:
            delta_reward = metrics_b["image_reward"]["mean"] - metrics_a["image_reward"]["mean"]
            comparison_entry["deltas"]["image_reward"] = float(delta_reward)
        
        if "quality_index" in metrics_a and "quality_index" in metrics_b:
            delta_quality = metrics_b["quality_index"] - metrics_a["quality_index"]
            comparison_entry["deltas"]["quality_index"] = float(delta_quality)
        
        # Стабильность (дисперсия CLIPScore)
        if "clip_score" in metrics_a and "clip_score" in metrics_b:
            delta_stability = metrics_b["clip_score"]["std"] - metrics_a["clip_score"]["std"]
            comparison_entry["deltas"]["stability"] = float(delta_stability)
        
        comparison["comparisons"].append(comparison_entry)
    
    # Сохраняем сравнение
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison_file = os.path.join(output_dir, f"comparison_{timestamp_str}.json")
    
    with open(comparison_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    print(f"Сравнение сохранено: {comparison_file}")
    
    return comparison
