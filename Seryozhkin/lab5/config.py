import os
from pathlib import Path

# Пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
VIDEOS_DIR = DATA_DIR / "videos"
DB_PATH = DATA_DIR / "brainrot.db"

# Кэш Hugging Face на диск H
HF_CACHE_DIR = BASE_DIR / "models_cache"
HF_CACHE_DIR.mkdir(exist_ok=True)

# Устанавливаем переменные окружения для кэша на диск H
os.environ["HF_HOME"] = str(HF_CACHE_DIR)
os.environ["HF_DATASETS_CACHE"] = str(HF_CACHE_DIR / "datasets")
os.environ["HF_HUB_CACHE"] = str(HF_CACHE_DIR / "hub")

# Создаем директории
DATA_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)
(HF_CACHE_DIR / "transformers").mkdir(exist_ok=True, parents=True)
(HF_CACHE_DIR / "datasets").mkdir(exist_ok=True, parents=True)
(HF_CACHE_DIR / "hub").mkdir(exist_ok=True, parents=True)

# Модели Hugging Face
CLIP_MODEL = "openai/clip-vit-large-patch14"
VIT_MODEL = "google/vit-base-patch16-224"
WHISPER_MODEL = "openai/whisper-large-v3"

# Параметры анализа
WINDOW_SIZE_SECONDS = 1.0
MAX_VIDEOS_TO_PARSE = 10

# VK API (если нужно)
VK_ACCESS_TOKEN = os.getenv("VK_ACCESS_TOKEN", "")

# Настройки сервера
HOST = "0.0.0.0"
PORT = 8000

