import aiohttp
import asyncio
from typing import List, Dict, Optional
import re
from urllib.parse import urlparse, parse_qs

class VKClipParser:
    """Парсер VK-клипов для получения видео URL в реальном времени"""
    
    def __init__(self):
        self.base_url = "https://vk.com"
        self.clips_url = "https://vk.com/clips"
        
    async def parse_clip_url(self, clip_url: str) -> Optional[Dict]:
        """Парсит URL клипа и извлекает информацию"""
        try:
            # Извлекаем ID клипа из URL
            # Формат: https://vk.com/clip{owner_id}_{clip_id}
            match = re.search(r'/clip(\d+)_(\d+)', clip_url)
            if not match:
                return None
                
            owner_id, clip_id = match.groups()
            
            return {
                "video_id": f"{owner_id}_{clip_id}",
                "owner_id": owner_id,
                "clip_id": clip_id,
                "url": clip_url
            }
        except Exception as e:
            print(f"Ошибка парсинга URL: {e}")
            return None
    
    async def get_clip_info(self, clip_url: str) -> Optional[Dict]:
        """Получает информацию о клипе через yt-dlp (работает с VK)"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'format': 'best[ext=mp4]/best',  # Выбираем лучший формат
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(clip_url, download=False)
                
                # Получаем прямой URL видео
                video_url = info.get('url', '')
                if not video_url and 'formats' in info:
                    # Пытаемся найти лучший формат
                    for fmt in info.get('formats', []):
                        if fmt.get('vcodec') != 'none' and fmt.get('url'):
                            video_url = fmt['url']
                            break
                
                return {
                    "video_id": info.get('id', ''),
                    "title": info.get('title', 'Без названия'),
                    "author": info.get('uploader', info.get('channel', 'Неизвестно')),
                    "duration": info.get('duration', 30),
                    "url": video_url or clip_url,  # Используем прямой URL или оригинальный
                    "thumbnail": info.get('thumbnail', ''),
                    "view_count": info.get('view_count', 0),
                    "original_url": clip_url
                }
        except Exception as e:
            print(f"Ошибка получения информации о клипе: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def parse_trending_clips(self, limit: int = 10) -> List[Dict]:
        """Парсит трендовые клипы"""
        # Для реального использования нужен VK API или парсинг страницы
        # Здесь возвращаем пустой список - пользователь должен указать URL вручную
        # Или можно использовать поиск через yt-dlp
        print(f"⚠️  Парсинг трендов требует VK API. Используйте ручной ввод URL.")
        return []

# Альтернативный парсер для TikTok (если нужно)
class TikTokParser:
    """Парсер TikTok видео"""
    
    async def parse_tiktok_url(self, tiktok_url: str) -> Optional[Dict]:
        """Парсит TikTok URL"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(tiktok_url, download=False)
                
                return {
                    "video_id": info.get('id', ''),
                    "title": info.get('title', ''),
                    "author": info.get('uploader', ''),
                    "duration": info.get('duration', 0),
                    "url": info.get('url', ''),
                    "thumbnail": info.get('thumbnail', ''),
                    "view_count": info.get('view_count', 0)
                }
        except Exception as e:
            print(f"Ошибка парсинга TikTok: {e}")
            return None

