# src/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import requests
import random
import time
from datetime import datetime
import json

app = FastAPI(
    title="VK Brainrot Detector API",
    description="API для анализа брейнорота в VK клипах",
    version="1.0.0"
)


class AnalyzeRequest(BaseModel):
    url: str
    deep_analysis: bool = False


class VideoInfo(BaseModel):
    url: str
    brainrot_index: float
    stim_density: float
    transition_rate: float
    meme_score: float
    analysis_time: float
    verdict: str


# Хранилище результатов (временное)
results_db = {}


def generate_brainrot_metrics(url: str) -> dict:
    """Генерирует демо-метрики для видео."""
    # Демо-логика анализа
    brainrot = random.uniform(0, 100)

    metrics = {
        "brainrot_index": round(brainrot, 2),
        "stim_density": round(random.uniform(0, 1), 3),
        "transition_rate": round(random.uniform(0, 10), 2),
        "meme_score": round(random.uniform(0, 1), 3),
        "audio_chaos": round(random.uniform(0, 1), 3),
        "visual_overload": round(random.uniform(0, 1), 3)
    }

    # Определяем вердикт
    if brainrot > 80:
        verdict = "🔴 КРИТИЧЕСКИЙ БРЕЙНОРОТ"
        metrics["risk_level"] = "HIGH"
    elif brainrot > 60:
        verdict = "🟠 ВЫСОКИЙ БРЕЙНОРОТ"
        metrics["risk_level"] = "MEDIUM_HIGH"
    elif brainrot > 40:
        verdict = "🟡 УМЕРЕННЫЙ БРЕЙНОРОТ"
        metrics["risk_level"] = "MEDIUM"
    elif brainrot > 20:
        verdict = "🔵 НИЗКИЙ БРЕЙНОРОТ"
        metrics["risk_level"] = "LOW"
    else:
        verdict = "🟢 НОРМАЛЬНЫЙ КОНТЕНТ"
        metrics["risk_level"] = "SAFE"

    metrics["verdict"] = verdict

    # Добавляем рекомендации
    if brainrot > 60:
        metrics["recommendation"] = "Рекомендуется ограничить просмотр"
    elif brainrot > 40:
        metrics["recommendation"] = "Умеренное воздействие"
    else:
        metrics["recommendation"] = "Безопасный контент"

    return metrics


def extract_video_id(url: str) -> str:
    """Извлекает ID видео из VK URL."""
    # Простая логика для демо
    if "video" in url:
        parts = url.split("video")[-1].replace("-", "_").strip("/")
        return f"vk_{parts}"
    return f"video_{hash(url) % 10000}"


@app.get("/")
async def root():
    return {
        "message": "VK Brainrot Detector API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "/analyze": "POST - Анализ видео",
            "/results": "GET - Все результаты",
            "/stats": "GET - Статистика",
            "/health": "GET - Проверка здоровья"
        },
        "note": "Это демо-версия. Реальный парсинг VK будет добавлен позже."
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "active_analyses": len(results_db)
    }


@app.post("/analyze", response_model=VideoInfo)
async def analyze_video(request: AnalyzeRequest):
    """Анализирует видео по URL."""
    try:
        start_time = time.time()

        # Генерируем ID для видео
        video_id = extract_video_id(request.url)

        # Если уже анализировали, возвращаем кэш
        if video_id in results_db:
            return results_db[video_id]

        # Генерируем метрики
        metrics = generate_brainrot_metrics(request.url)

        # Создаем ответ
        result = {
            "url": request.url,
            "brainrot_index": metrics["brainrot_index"],
            "stim_density": metrics["stim_density"],
            "transition_rate": metrics["transition_rate"],
            "meme_score": metrics["meme_score"],
            "analysis_time": round(time.time() - start_time, 2),
            "verdict": metrics["verdict"],
            "detailed_metrics": metrics
        }

        # Сохраняем в кэш
        results_db[video_id] = result

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/results")
async def get_all_results(limit: int = 20):
    """Возвращает все результаты анализов."""
    results = list(results_db.values())
    results.sort(key=lambda x: x.get("brainrot_index", 0), reverse=True)

    return {
        "total": len(results),
        "results": results[:limit],
        "average_brainrot": round(
            sum(r.get("brainrot_index", 0) for r in results) / len(results) if results else 0,
            2
        )
    }


@app.get("/stats")
async def get_stats():
    """Статистика анализа."""
    if not results_db:
        return {"message": "Нет данных для анализа"}

    results = list(results_db.values())
    brainrot_values = [r.get("brainrot_index", 0) for r in results]

    stats = {
        "total_videos": len(results),
        "average_brainrot": round(sum(brainrot_values) / len(brainrot_values), 2),
        "max_brainrot": round(max(brainrot_values), 2),
        "min_brainrot": round(min(brainrot_values), 2),
        "distribution": {
            "critical": len([v for v in brainrot_values if v > 80]),
            "high": len([v for v in brainrot_values if 60 < v <= 80]),
            "medium": len([v for v in brainrot_values if 40 < v <= 60]),
            "low": len([v for v in brainrot_values if 20 < v <= 40]),
            "safe": len([v for v in brainrot_values if v <= 20])
        }
    }

    return stats


@app.get("/analyze/batch")
async def analyze_batch(urls: str):
    """Анализирует несколько видео сразу."""
    url_list = [url.strip() for url in urls.split(",") if url.strip()]

    if not url_list:
        raise HTTPException(status_code=400, detail="Нет URL для анализа")

    if len(url_list) > 10:
        raise HTTPException(status_code=400, detail="Максимум 10 видео за раз")

    results = []
    for url in url_list:
        try:
            result = await analyze_video(AnalyzeRequest(url=url))
            results.append(result)
        except Exception as e:
            results.append({
                "url": url,
                "error": str(e),
                "brainrot_index": None
            })

    # Сортировка по индексу
    successful = [r for r in results if r.get("brainrot_index") is not None]
    successful.sort(key=lambda x: x["brainrot_index"], reverse=True)

    return {
        "total": len(results),
        "successful": len(successful),
        "top_brainrot": successful[:3] if successful else [],
        "all_results": results
    }


if __name__ == "__main__":
    print("=" * 50)
    print("VK Brainrot Detector запускается...")
    print("Откройте в браузере: http://localhost:8000")
    print("Документация: http://localhost:8000/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)