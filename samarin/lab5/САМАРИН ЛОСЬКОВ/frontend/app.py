"""
Flask приложение для интерфейса аналитики
"""

import os
import json
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path
import pandas as pd

app = Flask(__name__)
CORS(app)

# Пути
BASE_DIR = Path(__file__).parent.parent
RESULTS_DIR = BASE_DIR / "results"
VIDEOS_DIR = BASE_DIR / "outputs" / "videos"
BENCHMARK_DIR = RESULTS_DIR / "benchmark"
COMPARISONS_DIR = RESULTS_DIR / "comparisons"


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/api/videos')
def list_videos():
    """Список всех сгенерированных видео"""
    videos = []
    if VIDEOS_DIR.exists():
        for video_file in VIDEOS_DIR.glob("*.mp4"):
            videos.append({
                "name": video_file.name,
                "path": f"/api/videos/file/{video_file.name}",
                "size": video_file.stat().st_size
            })
    return jsonify(videos)


@app.route('/api/videos/file/<filename>')
def serve_video(filename):
    """Отдача видео файла"""
    return send_from_directory(str(VIDEOS_DIR), filename)


@app.route('/api/metrics/<video_name>')
def get_metrics(video_name):
    """Получение метрик для видео"""
    video_stem = Path(video_name).stem
    metrics_file = RESULTS_DIR / f"{video_stem}_metrics.json"
    
    if metrics_file.exists():
        with open(metrics_file, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    else:
        return jsonify({"error": "Метрики не найдены"}), 404


@app.route('/api/benchmark/runs')
def list_benchmark_runs():
    """Список всех запусков бенчмарка"""
    runs = []
    if BENCHMARK_DIR.exists():
        for run_file in BENCHMARK_DIR.glob("benchmark_*.json"):
            with open(run_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                runs.append({
                    "file": run_file.name,
                    "timestamp": data.get("timestamp", ""),
                    "model_version": data.get("model_version", "unknown"),
                    "num_prompts": len(data.get("prompts", []))
                })
    
    # Сортируем по времени (новые первыми)
    runs.sort(key=lambda x: x["timestamp"], reverse=True)
    return jsonify(runs)


@app.route('/api/benchmark/<run_file>')
def get_benchmark_run(run_file):
    """Получение данных конкретного запуска бенчмарка"""
    run_path = BENCHMARK_DIR / run_file
    
    if run_path.exists():
        with open(run_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    else:
        return jsonify({"error": "Запуск не найден"}), 404


@app.route('/api/comparisons')
def list_comparisons():
    """Список всех сравнений моделей"""
    comparisons = []
    if COMPARISONS_DIR.exists():
        for comp_file in COMPARISONS_DIR.glob("comparison_*.json"):
            with open(comp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                comparisons.append({
                    "file": comp_file.name,
                    "timestamp": data.get("timestamp", ""),
                    "model_a": data.get("model_a", "unknown"),
                    "model_b": data.get("model_b", "unknown"),
                    "num_comparisons": len(data.get("comparisons", []))
                })
    
    comparisons.sort(key=lambda x: x["timestamp"], reverse=True)
    return jsonify(comparisons)


@app.route('/api/comparisons/<comp_file>')
def get_comparison(comp_file):
    """Получение данных сравнения"""
    comp_path = COMPARISONS_DIR / comp_file
    
    if comp_path.exists():
        with open(comp_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    else:
        return jsonify({"error": "Сравнение не найдено"}), 404


@app.route('/api/analytics/summary')
def get_analytics_summary():
    """Сводная аналитика по всем метрикам"""
    summary = {
        "total_videos": 0,
        "total_benchmark_runs": 0,
        "total_comparisons": 0,
        "average_quality_index": 0.0,
        "average_clip_score": 0.0
    }
    
    # Подсчитываем видео
    if VIDEOS_DIR.exists():
        summary["total_videos"] = len(list(VIDEOS_DIR.glob("*.mp4")))
    
    # Подсчитываем запуски бенчмарка
    if BENCHMARK_DIR.exists():
        summary["total_benchmark_runs"] = len(list(BENCHMARK_DIR.glob("benchmark_*.json")))
    
    # Подсчитываем сравнения
    if COMPARISONS_DIR.exists():
        summary["total_comparisons"] = len(list(COMPARISONS_DIR.glob("comparison_*.json")))
    
    # Собираем метрики из всех файлов
    quality_indices = []
    clip_scores = []
    
    for metrics_file in RESULTS_DIR.glob("*_metrics.json"):
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "quality_index" in data:
                    quality_indices.append(data["quality_index"])
                if "clip_score" in data and "mean" in data["clip_score"]:
                    clip_scores.append(data["clip_score"]["mean"])
        except:
            continue
    
    if quality_indices:
        summary["average_quality_index"] = sum(quality_indices) / len(quality_indices)
    
    if clip_scores:
        summary["average_clip_score"] = sum(clip_scores) / len(clip_scores)
    
    return jsonify(summary)


if __name__ == '__main__':
    # Создаём необходимые директории
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    COMPARISONS_DIR.mkdir(parents=True, exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
