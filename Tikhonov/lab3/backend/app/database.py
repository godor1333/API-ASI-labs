from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import os
import time
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://memeuser:memepass@db:5432/memedb"
)

# Добавляем параметры для более надежного подключения
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=300,    # Переподключение каждые 5 минут
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализация базы данных с повторными попытками"""
    from .models import Base
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Попытка подключения к БД (попытка {attempt + 1}/{max_retries})")
            Base.metadata.create_all(bind=engine)
            logger.info("База данных успешно инициализирована")
            return
        except OperationalError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Ошибка подключения: {e}. Повтор через {retry_delay} сек...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Не удалось подключиться к БД после {max_retries} попыток")
                raise

