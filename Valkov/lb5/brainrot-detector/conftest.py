import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import os
from pathlib import Path

from database import Base, get_db, VideoAnalysis
from main import app

# Создаем временную базу данных для тестов
TEST_DB_PATH = tempfile.mktemp(suffix='.db')

# Создаем engine для тестовой БД
test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Создаем таблицы
Base.metadata.create_all(test_engine)

# Создаем сессию для тестов
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Переопределяем get_db для использования тестовой БД"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Фикстура для создания тестовой сессии БД"""
    Base.metadata.create_all(test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


def create_mocks():
    """Создает и настраивает мок-объекты"""
    mock_parser = Mock()
    mock_tiktok_parser = Mock()
    mock_analyzer = Mock()
    
    # Настраиваем async методы
    mock_parser.get_clip_info = AsyncMock(return_value={
        "url": "https://vk.com/clip123456_789012",
        "video_id": "123456_789012",
        "title": "Test Video",
        "author": "Test Author",
        "duration": 30.0
    })
    mock_parser.parse_trending_clips = AsyncMock(return_value=[
        {
            "url": "https://vk.com/clip111_222",
            "video_id": "111_222",
            "title": "Trending Video 1",
            "author": "Author 1",
            "duration": 25.0
        },
        {
            "url": "https://vk.com/clip333_444",
            "video_id": "333_444",
            "title": "Trending Video 2",
            "author": "Author 2",
            "duration": 35.0
        }
    ])
    
    mock_tiktok_parser.parse_tiktok_url = AsyncMock(return_value={
        "url": "https://tiktok.com/@test/video/123",
        "video_id": "tiktok_123",
        "title": "TikTok Video",
        "author": "TikTok Author",
        "duration": 20.0
    })
    
    mock_analyzer.analyze_video = AsyncMock(return_value={
        "brainrot_index": 65.5,
        "metrics": {
            "transition_density": 0.8,
            "pattern_variability": 0.7,
            "speech_rate": 5.5
        },
        "transcript": "Test transcript text"
    })
    
    return mock_parser, mock_tiktok_parser, mock_analyzer


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура для создания тестового клиента"""
    # Переопределяем get_db
    app.dependency_overrides[get_db] = override_get_db
    
    # Создаем моки
    mock_parser, mock_tiktok_parser, mock_analyzer = create_mocks()
    
    # Устанавливаем моки в main модуль перед созданием клиента
    # (переопределяем то, что может быть создано в lifespan)
    import main
    main.parser = mock_parser
    main.tiktok_parser = mock_tiktok_parser
    main.analyzer = mock_analyzer
    
    # Создаем клиент (lifespan будет вызван, но мы уже установили моки)
    # Используем raise_server_exceptions=False чтобы игнорировать ошибки lifespan
    test_client = TestClient(app, raise_server_exceptions=False)
    
    # Убеждаемся, что моки все еще установлены (на случай если lifespan их перезаписал)
    main.parser = mock_parser
    main.tiktok_parser = mock_tiktok_parser
    main.analyzer = mock_analyzer
    
    yield test_client
    
    # Очистка после теста
    app.dependency_overrides.clear()
    main.parser = None
    main.tiktok_parser = None
    main.analyzer = None



