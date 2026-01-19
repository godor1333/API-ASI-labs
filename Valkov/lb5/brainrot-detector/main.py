from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from contextlib import asynccontextmanager
import json
import asyncio

from database import get_db, VideoAnalysis, Base, engine
from vk_parser import VKClipParser, TikTokParser
from video_analyzer import VideoAnalyzer
from config import MAX_VIDEOS_TO_PARSE

# Глобальные переменные для хранения инициализированных объектов
parser = None
tiktok_parser = None
analyzer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global parser, tiktok_parser, analyzer
    
    # Startup
    print("🚀 Инициализация приложения...")
    parser = VKClipParser()
    tiktok_parser = TikTokParser()
    analyzer = VideoAnalyzer()
    print("✅ Приложение готово к работе")
    
    yield
    
    # Shutdown
    try:
        print("🛑 Завершение работы приложения...")
        # Очистка ресурсов (если необходимо)
        if analyzer:
            # Освобождаем память моделей
            if hasattr(analyzer, 'clip_model'):
                del analyzer.clip_model
            if hasattr(analyzer, 'vit_model'):
                del analyzer.vit_model
            if hasattr(analyzer, 'whisper_model'):
                del analyzer.whisper_model
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        print("✅ Приложение завершено")
    except asyncio.CancelledError:
        # Обрабатываем отмену gracefully
        print("🛑 Завершение работы приложения (прервано)...")
        pass

app = FastAPI(title="Brainrot Detector", version="1.0.0", lifespan=lifespan)

# Фоновая задача для анализа
async def analyze_video_background(video_url: str, video_info: dict, db: Session):
    """Фоновая задача для анализа видео"""
    if not analyzer:
        print("Ошибка: анализатор не инициализирован")
        return
    
    try:
        result = await analyzer.analyze_video(
            video_url, 
            video_info.get("duration", 30.0)
        )
        
        if "error" in result:
            print(f"Ошибка анализа: {result['error']}")
            return
        
        # Сохраняем в БД
        analysis = VideoAnalysis(
            video_url=video_info.get("url", video_url),
            video_id=video_info.get("video_id", ""),
            author=video_info.get("author", ""),
            title=video_info.get("title", ""),
            brainrot_index=result.get("brainrot_index", 0.0),
            metrics=json.dumps(result.get("metrics", {})),
            transcript=result.get("transcript", ""),
            memes_detected=json.dumps([])
        )
        
        db.add(analysis)
        db.commit()
        print(f"Анализ сохранен: {video_info.get('title', video_url)}")
        
    except asyncio.CancelledError:
        # Задача отменена (например, при перезагрузке сервера) - это нормально
        print("⚠️  Анализ видео прерван (перезагрузка сервера)")
        return  # Просто выходим, не пробрасываем исключение
    except Exception as e:
        print(f"Ошибка анализа видео: {e}")
        import traceback
        traceback.print_exc()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с админкой"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Brainrot Detector - Админка</title>
        <meta charset="utf-8">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #333;
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            .controls {
                display: flex;
                gap: 15px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }
            input, button {
                padding: 12px 20px;
                border: 2px solid #ddd;
                border-radius: 10px;
                font-size: 16px;
            }
            input {
                flex: 1;
                min-width: 300px;
            }
            button {
                background: #667eea;
                color: white;
                border: none;
                cursor: pointer;
                transition: all 0.3s;
            }
            button:hover {
                background: #5568d3;
                transform: translateY(-2px);
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
            }
            .stat-value {
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
            }
            .stat-label {
                opacity: 0.9;
                font-size: 0.9em;
            }
            .video-list {
                margin-top: 30px;
            }
            .video-item {
                background: #f8f9fa;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .video-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            .brainrot-badge {
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                color: white;
            }
            .high { background: #e74c3c; }
            .medium { background: #f39c12; }
            .low { background: #27ae60; }
            .loading {
                text-align: center;
                padding: 40px;
                color: #667eea;
                font-size: 1.2em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 Brainrot Detector - Админка</h1>
            
            <div class="controls">
                <input type="text" id="videoUrl" placeholder="Вставьте URL VK-клипа или TikTok (например: https://vk.com/clip123456_789012)">
                <button onclick="analyzeVideo()">Анализировать</button>
                <button onclick="parseTrending()">Парсить тренды</button>
                <button onclick="loadAnalyses()">Обновить данные</button>
            </div>
            <div id="status" style="margin-top: 10px; padding: 10px; border-radius: 5px; display: none;"></div>
            
            <div class="stats" id="stats">
                <div class="stat-card">
                    <div class="stat-label">Всего видео</div>
                    <div class="stat-value" id="totalVideos">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Средний индекс</div>
                    <div class="stat-value" id="avgIndex">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Макс. индекс</div>
                    <div class="stat-value" id="maxIndex">0</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Топ автор</div>
                    <div class="stat-value" id="topAuthor">-</div>
                </div>
            </div>
            
            <div id="chart" style="height: 400px; margin: 30px 0;"></div>
            
            <div class="video-list" id="videoList">
                <div class="loading">Загрузка данных...</div>
            </div>
        </div>
        
        <script>
            async function analyzeVideo() {
                const url = document.getElementById('videoUrl').value;
                if (!url) {
                    showStatus('Введите URL', 'error');
                    return;
                }
                
                showStatus('Запуск анализа...', 'info');
                
                try {
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({url: url})
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        showStatus('✅ Анализ запущен! Обновите данные через минуту.', 'success');
                        document.getElementById('videoUrl').value = '';
                    } else {
                        showStatus('❌ Ошибка: ' + (data.detail || 'Неизвестная ошибка'), 'error');
                    }
                } catch (e) {
                    showStatus('❌ Ошибка соединения', 'error');
                }
            }
            
            function showStatus(message, type) {
                const statusEl = document.getElementById('status');
                statusEl.textContent = message;
                statusEl.style.display = 'block';
                statusEl.style.background = type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1';
                statusEl.style.color = type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460';
                setTimeout(() => {
                    if (type !== 'info') {
                        statusEl.style.display = 'none';
                    }
                }, 5000);
            }
            
            async function parseTrending() {
                const response = await fetch('/api/parse_trending', {method: 'POST'});
                if (response.ok) {
                    alert('Парсинг трендов запущен! Обновите данные через минуту.');
                }
            }
            
            async function loadAnalyses() {
                const response = await fetch('/api/analyses');
                const data = await response.json();
                
                // Статистика
                document.getElementById('totalVideos').textContent = data.length;
                if (data.length > 0) {
                    const avg = data.reduce((s, v) => s + v.brainrot_index, 0) / data.length;
                    document.getElementById('avgIndex').textContent = avg.toFixed(1);
                    const max = Math.max(...data.map(v => v.brainrot_index));
                    document.getElementById('maxIndex').textContent = max.toFixed(1);
                    
                    // Топ автор
                    const authors = {};
                    data.forEach(v => {
                        authors[v.author] = (authors[v.author] || 0) + 1;
                    });
                    const topAuthor = Object.entries(authors).sort((a,b) => b[1] - a[1])[0];
                    document.getElementById('topAuthor').textContent = topAuthor ? topAuthor[0].substring(0, 10) : '-';
                }
                
                // График
                if (data.length > 0) {
                    const trace = {
                        x: data.map((v, i) => i + 1),
                        y: data.map(v => v.brainrot_index),
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Brainrot Index',
                        line: {color: '#667eea', width: 2}
                    };
                    Plotly.newPlot('chart', [trace], {
                        title: 'BRAINROT INDEX по времени',
                        xaxis: {title: 'Видео #'},
                        yaxis: {title: 'Индекс'},
                        paper_bgcolor: 'rgba(0,0,0,0)',
                        plot_bgcolor: 'rgba(0,0,0,0)'
                    });
                }
                
                // Список видео
                const listHtml = data.map(v => {
                    const level = v.brainrot_index > 70 ? 'high' : v.brainrot_index > 40 ? 'medium' : 'low';
                    return `
                        <div class="video-item">
                            <div class="video-header">
                                <strong>${v.title || v.video_id}</strong>
                                <span class="brainrot-badge ${level}">${v.brainrot_index.toFixed(1)}</span>
                            </div>
                            <div style="color: #666; font-size: 0.9em;">
                                Автор: ${v.author || 'Неизвестно'} | 
                                Метрики: Переходы ${v.metrics.transition_density.toFixed(2)}, 
                                Стимы ${v.metrics.pattern_variability.toFixed(2)}, 
                                Речь ${v.metrics.speech_rate.toFixed(1)} слов/с
                            </div>
                            ${v.transcript ? `<div style="margin-top: 10px; color: #888; font-size: 0.85em;">${v.transcript.substring(0, 200)}...</div>` : ''}
                        </div>
                    `;
                }).join('');
                
                document.getElementById('videoList').innerHTML = listHtml || '<div class="loading">Нет данных</div>';
            }
            
            // Загружаем данные при загрузке страницы
            loadAnalyses();
            setInterval(loadAnalyses, 30000); // Обновление каждые 30 секунд
        </script>
    </body>
    </html>
    """

@app.post("/api/analyze")
async def analyze_video_endpoint(data: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """API endpoint для анализа одного видео"""
    if not parser or not tiktok_parser or not analyzer:
        raise HTTPException(status_code=503, detail="Приложение еще инициализируется")
    
    video_url = data.get("url")
    if not video_url:
        raise HTTPException(status_code=400, detail="URL не указан")
    
    # Парсим URL
    if "vk.com" in video_url or "vk.ru" in video_url or "vkvideo.ru" in video_url:
        video_info = await parser.get_clip_info(video_url)
    elif "tiktok.com" in video_url:
        video_info = await tiktok_parser.parse_tiktok_url(video_url)
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемый URL")
    
    if not video_info:
        raise HTTPException(status_code=400, detail="Не удалось получить информацию о видео")
    
    # Проверяем, не анализировали ли уже
    existing = db.query(VideoAnalysis).filter_by(video_url=video_info.get("url", video_url)).first()
    if existing:
        return {"message": "Видео уже проанализировано", "analysis_id": existing.id}
    
    # Запускаем анализ в фоне
    background_tasks.add_task(analyze_video_background, video_info.get("url", video_url), video_info, db)
    
    return {"message": "Анализ запущен", "video_info": video_info}

@app.post("/api/parse_trending")
async def parse_trending_endpoint(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """API endpoint для парсинга трендовых видео"""
    if not parser or not analyzer:
        raise HTTPException(status_code=503, detail="Приложение еще инициализируется")
    
    # Парсим трендовые клипы
    clips = await parser.parse_trending_clips(limit=MAX_VIDEOS_TO_PARSE)
    
    if not clips:
        return {"message": "Парсинг трендов требует VK API. Вставьте URL вручную.", "count": 0}
    
    # Запускаем анализ каждого в фоне
    for clip_info in clips:
        if clip_info.get("url"):
            background_tasks.add_task(analyze_video_background, clip_info["url"], clip_info, db)
    
    return {"message": f"Запущен анализ {len(clips)} видео", "count": len(clips)}

@app.get("/api/analyses")
async def get_analyses(db: Session = Depends(get_db), limit: int = 100):
    """Получить все анализы"""
    analyses = db.query(VideoAnalysis).order_by(VideoAnalysis.created_at.desc()).limit(limit).all()
    return [analysis.to_dict() for analysis in analyses]

@app.get("/api/analyses/{analysis_id}")
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Получить конкретный анализ"""
    analysis = db.query(VideoAnalysis).filter_by(id=analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Анализ не найден")
    return analysis.to_dict()

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Получить статистику"""
    analyses = db.query(VideoAnalysis).all()
    
    if not analyses:
        return {
            "total": 0,
            "avg_brainrot": 0,
            "max_brainrot": 0,
            "min_brainrot": 0
        }
    
    brainrot_values = [a.brainrot_index for a in analyses]
    
    return {
        "total": len(analyses),
        "avg_brainrot": sum(brainrot_values) / len(brainrot_values),
        "max_brainrot": max(brainrot_values),
        "min_brainrot": min(brainrot_values)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

