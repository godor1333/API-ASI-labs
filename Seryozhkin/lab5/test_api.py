"""
REST API тесты для brainrot-detector
"""
import pytest
from fastapi import status


class TestRootEndpoint:
    """Тесты для корневого эндпоинта GET /"""
    
    def test_root_endpoint_returns_html(self, client):
        """Тест: корневой эндпоинт возвращает HTML страницу"""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert "Brainrot Detector" in response.text
        assert "Админка" in response.text


class TestAnalyzeEndpoint:
    """Тесты для эндпоинта POST /api/analyze"""
    
    def test_analyze_vk_video_success(self, client):
        """Тест: успешный анализ VK видео"""
        response = client.post(
            "/api/analyze",
            json={"url": "https://vk.com/clip123456_789012"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "video_info" in data
        assert data["message"] == "Анализ запущен"
        assert data["video_info"]["title"] == "Test Video"
    
    def test_analyze_tiktok_video_success(self, client):
        """Тест: успешный анализ TikTok видео"""
        response = client.post(
            "/api/analyze",
            json={"url": "https://tiktok.com/@test/video/123"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "video_info" in data
        assert data["video_info"]["title"] == "TikTok Video"
    
    def test_analyze_without_url(self, client):
        """Тест: ошибка при отсутствии URL"""
        response = client.post(
            "/api/analyze",
            json={}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "URL не указан" in response.json()["detail"]
    
    def test_analyze_invalid_url(self, client):
        """Тест: ошибка при неподдерживаемом URL"""
        response = client.post(
            "/api/analyze",
            json={"url": "https://youtube.com/watch?v=test"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Неподдерживаемый URL" in response.json()["detail"]


class TestParseTrendingEndpoint:
    """Тесты для эндпоинта POST /api/parse_trending"""
    
    def test_parse_trending_success(self, client):
        """Тест: успешный парсинг трендовых видео"""
        response = client.post("/api/parse_trending")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "count" in data
        assert data["count"] == 2
    
    def test_parse_trending_empty_result(self, client):
        """Тест: парсинг трендов возвращает пустой результат"""
        from unittest.mock import AsyncMock
        from main import parser
        parser.parse_trending_clips = AsyncMock(return_value=[])
        
        response = client.post("/api/parse_trending")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 0


class TestGetAnalysesEndpoint:
    """Тесты для эндпоинта GET /api/analyses"""
    
    def test_get_analyses_with_limit(self, client, db_session):
        """Тест: получение анализов с лимитом"""
        from database import VideoAnalysis
        import json
        
        # Создаем несколько анализов
        for i in range(5):
            analysis = VideoAnalysis(
                video_url=f"https://vk.com/clip{i}",
                video_id=f"clip{i}",
                title=f"Video {i}",
                author=f"Author {i}",
                brainrot_index=50.0 + i,
                metrics=json.dumps({"transition_density": 0.5}),
                transcript="Test",
                memes_detected=json.dumps([])
            )
            db_session.add(analysis)
        db_session.commit()
        
        response = client.get("/api/analyses?limit=3")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3


class TestGetAnalysisByIdEndpoint:
    """Тесты для эндпоинта GET /api/analyses/{analysis_id}"""
    
    def test_get_analysis_by_id_not_found(self, client):
        """Тест: анализ не найден"""
        response = client.get("/api/analyses/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "не найден" in response.json()["detail"]
