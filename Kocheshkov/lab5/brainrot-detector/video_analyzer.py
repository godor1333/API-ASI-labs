import torch
import numpy as np
import os
import ssl
from transformers import CLIPProcessor, CLIPModel, ViTImageProcessor, ViTForImageClassification, WhisperProcessor, WhisperForConditionalGeneration
from PIL import Image
import cv2
from typing import List, Dict, Tuple, Optional
import asyncio
import aiohttp
from config import CLIP_MODEL, VIT_MODEL, WHISPER_MODEL, WINDOW_SIZE_SECONDS, HF_CACHE_DIR

# Устанавливаем кэш Hugging Face на диск H
os.environ["HF_HOME"] = str(HF_CACHE_DIR)
os.environ["HF_DATASETS_CACHE"] = str(HF_CACHE_DIR / "datasets")
os.environ["HF_HUB_CACHE"] = str(HF_CACHE_DIR / "hub")

class VideoAnalyzer:
    """Анализатор видео для вычисления брейнорот-индекса"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Используется устройство: {self.device}")
        
        # Загружаем модели с кэшем на диск H
        cache_dir = str(HF_CACHE_DIR / "hub")
        print(f"Загрузка моделей в кэш: {cache_dir}")
        
        print("Загрузка CLIP модели...")
        self.clip_model = CLIPModel.from_pretrained(CLIP_MODEL, cache_dir=cache_dir).to(self.device)
        self.clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL, cache_dir=cache_dir)
        
        print("Загрузка ViT модели...")
        self.vit_model = ViTForImageClassification.from_pretrained(VIT_MODEL, cache_dir=cache_dir).to(self.device)
        self.vit_processor = ViTImageProcessor.from_pretrained(VIT_MODEL, cache_dir=cache_dir)
        
        print("Загрузка Whisper модели...")
        self.whisper_processor = WhisperProcessor.from_pretrained(WHISPER_MODEL, cache_dir=cache_dir)
        self.whisper_model = WhisperForConditionalGeneration.from_pretrained(WHISPER_MODEL, cache_dir=cache_dir).to(self.device)
        
    async def download_video_stream(self, video_url: str) -> Optional[bytes]:
        """Скачивает видео по URL (только для анализа, не сохраняет)"""
        try:
            print(f"📥 Начало загрузки видео: {video_url[:100]}...")
            
            # Используем yt-dlp для получения прямого URL, если это не прямой URL
            if not video_url.startswith(('http://', 'https://')):
                print("⚠️  Неверный формат URL")
                return None
            
            # Проверяем, это прямой URL видео или нужна обработка через yt-dlp
            if any(domain in video_url for domain in ['vk.com', 'vk.ru', 'vkvideo.ru', 'tiktok.com', 'youtube.com']):
                # Используем yt-dlp для скачивания видео напрямую во временный файл
                print("🔧 Используем yt-dlp для скачивания видео...")
                import yt_dlp
                import tempfile
                
                # Создаем временный файл для видео
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                    tmp_path = tmp_file.name
                
                def download_with_ytdlp(url, output_path):
                    """Синхронная функция для скачивания через yt-dlp"""
                    ydl_opts = {
                        'quiet': False,  # Показываем прогресс для отладки
                        'no_warnings': False,
                        'format': 'best[ext=mp4]/best[height<=720]/best',  # Предпочитаем MP4, ограничиваем высоту
                        'outtmpl': output_path,
                        'noplaylist': True,
                        'extractaudio': False,
                        'postprocessors': [],
                        'verbose': True,  # Включаем подробный вывод
                    }
                    try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])
                    except Exception as e:
                        # Пробрасываем исключение с более детальной информацией
                        raise Exception(f"yt-dlp error: {str(e)}")
                
                try:
                    # Запускаем синхронный yt-dlp в executor, чтобы не блокировать event loop
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, download_with_ytdlp, video_url, tmp_path)
                    
                    # Читаем скачанное видео
                    if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
                        with open(tmp_path, 'rb') as f:
                            content = f.read()
                        os.unlink(tmp_path)
                        
                        if len(content) > 500 * 1024 * 1024:
                            print("⚠️  Видео слишком большое, пропускаем")
                            return None
                        if len(content) == 0:
                            print("⚠️  Получен пустой файл")
                            return None
                        
                        # Проверяем, что это действительно видео (проверка сигнатуры)
                        if content[:4] == b'\x00\x00\x00\x18ftyp' or content[:4] == b'\x00\x00\x00\x20ftyp' or content[:12] == b'RIFF' + b'\x00' * 4 + b'AVI ':
                            print(f"✅ Видео скачано через yt-dlp: {len(content) / 1024 / 1024:.2f} МБ")
                            return content
                        else:
                            # Проверяем другие видеоформаты
                            if b'ftyp' in content[:100] or b'RIFF' in content[:20] or b'moov' in content[:100]:
                                print(f"✅ Видео скачано через yt-dlp: {len(content) / 1024 / 1024:.2f} МБ")
                                return content
                            else:
                                print("⚠️  Скачанный файл не является видеофайлом")
                                return None
                    else:
                        print("⚠️  yt-dlp не смог скачать видео")
                        return None
                        
                except Exception as e:
                    print(f"⚠️  Ошибка при скачивании через yt-dlp: {e}")
                    import traceback
                    traceback.print_exc()
                    # Очищаем временный файл в случае ошибки
                    if os.path.exists(tmp_path):
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass
                    return None
            else:
                # Для прямых URL используем обычную загрузку
                direct_url = video_url
                print(f"📎 Используем прямой URL: {direct_url[:100]}...")
                
                # Заголовки для CDN запросов (особенно для VK CDN)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Referer': 'https://vk.com/',
                }
                
                # Скачиваем видео
                print("⏬ Начинаем скачивание...")
                # Отключаем проверку SSL-сертификата для работы с vkvideo.ru и подобными сайтами
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                connector = aiohttp.TCPConnector(ssl=ssl_context)
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(
                        direct_url, 
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=300),
                        allow_redirects=True
                    ) as response:
                        print(f"📊 HTTP статус: {response.status}")
                        if response.status == 200:
                            # Ограничиваем размер для безопасности (макс 500 МБ)
                            try:
                                content = await response.read()
                            except asyncio.CancelledError:
                                print("⚠️  Загрузка видео прервана (отмена задачи)")
                                return None  # Задача отменена, возвращаем None
                            
                            if len(content) > 500 * 1024 * 1024:
                                print("⚠️  Видео слишком большое, пропускаем")
                                return None
                            if len(content) == 0:
                                print("⚠️  Получен пустой файл")
                                return None
                            
                            # Проверяем, что это действительно видео
                            if content[:4] == b'\x00\x00\x00\x18ftyp' or content[:4] == b'\x00\x00\x00\x20ftyp' or content[:12] == b'RIFF' + b'\x00' * 4 + b'AVI ':
                                print(f"✅ Видео загружено: {len(content) / 1024 / 1024:.2f} МБ")
                                return content
                            elif b'ftyp' in content[:100] or b'RIFF' in content[:20] or b'moov' in content[:100]:
                                print(f"✅ Видео загружено: {len(content) / 1024 / 1024:.2f} МБ")
                                return content
                            else:
                                print("⚠️  Загруженный файл не является видеофайлом (возможно, HTML страница)")
                                return None
                        else:
                            try:
                                error_text = await response.text()
                            except asyncio.CancelledError:
                                print("⚠️  Загрузка видео прервана (отмена задачи)")
                                return None
                            print(f"⚠️  Ошибка HTTP {response.status} при загрузке видео")
                            print(f"⚠️  Ответ сервера: {error_text[:200]}")
                            return None
        except asyncio.CancelledError:
            # Задача отменена (например, при перезагрузке сервера) - это нормально
            print("⚠️  Загрузка видео отменена")
            return None
        except aiohttp.ClientError as e:
            print(f"⚠️  Ошибка сети при загрузке видео: {type(e).__name__}: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Ошибка загрузки видео: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        return None
    
    def extract_frames(self, video_data: bytes, fps: float = 1.0) -> List[Image.Image]:
        """Извлекает кадры из видео (1 кадр в секунду)"""
        frames = []
        import tempfile
        import subprocess
        
        tmp_path = None
        converted_path = None
        try:
            # Создаем временный файл для исходного видео
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                tmp_file.write(video_data)
                tmp_path = tmp_file.name
            
            # Пытаемся использовать ffmpeg для конвертации в правильный формат
            # Это помогает с проблемами декодирования H.264
            try:
                # Создаем конвертированный файл
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as converted_file:
                    converted_path = converted_file.name
                
                # Конвертируем через ffmpeg для исправления проблем с кодеком
                result = subprocess.run([
                    'ffmpeg', '-y', '-i', tmp_path,
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                    '-c:a', 'aac', '-b:a', '128k',
                    '-movflags', '+faststart',
                    converted_path
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0 and os.path.exists(converted_path) and os.path.getsize(converted_path) > 0:
                    # Используем конвертированный файл
                    video_file = converted_path
                    print("✅ Видео конвертировано через ffmpeg")
                else:
                    # Если ffmpeg не сработал, используем оригинал
                    video_file = tmp_path
                    if result.stderr:
                        print(f"⚠️  ffmpeg предупреждение: {result.stderr[:200]}")
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
                # Если ffmpeg не найден или ошибка, используем оригинальный файл
                video_file = tmp_path
                if isinstance(e, FileNotFoundError):
                    print("⚠️  ffmpeg не найден, используем прямое чтение видео (может быть медленнее)")
                else:
                    print(f"⚠️  Ошибка конвертации через ffmpeg: {e}, используем оригинальный файл")
            
            # Извлекаем кадры через OpenCV
            cap = cv2.VideoCapture(video_file)
            if not cap.isOpened():
                print("⚠️  Не удалось открыть видеофайл")
                return []
            
            frame_rate = cap.get(cv2.CAP_PROP_FPS) or 30
            frame_interval = int(frame_rate / fps) if fps > 0 else 1
            
            frame_count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(Image.fromarray(frame_rgb))
                
                frame_count += 1
            
            cap.release()
            print(f"✅ Извлечено кадров: {len(frames)}")
            
        except Exception as e:
            print(f"⚠️  Ошибка извлечения кадров: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Очищаем временные файлы
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            if converted_path and os.path.exists(converted_path):
                try:
                    os.unlink(converted_path)
                except:
                    pass
        
        return frames
    
    def get_clip_embeddings(self, frames: List[Image.Image]) -> np.ndarray:
        """Получает CLIP эмбеддинги для кадров"""
        embeddings = []
        
        for frame in frames:
            inputs = self.clip_processor(images=frame, return_tensors="pt").to(self.device)
            with torch.no_grad():
                image_features = self.clip_model.get_image_features(**inputs)
                embeddings.append(image_features.cpu().numpy())
        
        return np.array(embeddings)
    
    def classify_visual_patterns(self, frames: List[Image.Image]) -> List[Dict]:
        """Классифицирует визуальные паттерны с помощью ViT"""
        patterns = []
        
        for frame in frames:
            inputs = self.vit_processor(images=frame, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.vit_model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
                
                # Получаем топ-3 предсказания
                top_probs, top_indices = torch.topk(probs, 3)
                
                pattern = {
                    "top_classes": [
                        {
                            "class": self.vit_model.config.id2label[idx.item()],
                            "probability": prob.item()
                        }
                        for prob, idx in zip(top_probs[0], top_indices[0])
                    ]
                }
                patterns.append(pattern)
        
        return patterns
    
    def transcribe_audio(self, video_data: bytes) -> Dict:
        """Транскрибирует аудио с помощью Whisper"""
        import tempfile
        import subprocess
        
        tmp_video_path = None
        tmp_audio_path = None
        try:
            # Сохраняем видео во временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
                tmp_video.write(video_data)
                tmp_video_path = tmp_video.name
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_audio:
                tmp_audio_path = tmp_audio.name
            
            # Конвертируем видео в аудио через ffmpeg
            try:
                # Проверяем наличие ffmpeg
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
                
                result = subprocess.run([
                    'ffmpeg', '-i', tmp_video_path, 
                    '-ar', '16000', '-ac', '1', 
                    '-y', tmp_audio_path
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode != 0:
                    print(f"⚠️  ffmpeg ошибка: {result.stderr[:500]}")
                    return {"transcript": "", "word_count": 0}
                
                if not os.path.exists(tmp_audio_path) or os.path.getsize(tmp_audio_path) == 0:
                    print("⚠️  ffmpeg не создал аудиофайл")
                    return {"transcript": "", "word_count": 0}
                
                # Загружаем аудио
                import librosa
                audio_array, sr = librosa.load(tmp_audio_path, sr=16000)
                
                if len(audio_array) == 0:
                    print("⚠️  Аудиофайл пуст")
                    return {"transcript": "", "word_count": 0}
                
                # Транскрибируем
                inputs = self.whisper_processor(audio_array, sampling_rate=sr, return_tensors="pt").to(self.device)
                with torch.no_grad():
                    generated_ids = self.whisper_model.generate(**inputs)
                
                transcript = self.whisper_processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
                
                return {
                    "transcript": transcript,
                    "word_count": len(transcript.split()) if transcript else 0
                }
                
            except FileNotFoundError:
                print("⚠️  ffmpeg не найден. Установите ffmpeg для транскрипции аудио.")
                return {"transcript": "", "word_count": 0}
            except subprocess.TimeoutExpired:
                print("⚠️  Таймаут конвертации аудио через ffmpeg")
                return {"transcript": "", "word_count": 0}
            except ImportError as e:
                print(f"⚠️  librosa не установлен: {e}")
                return {"transcript": "", "word_count": 0}
            except Exception as e:
                print(f"⚠️  Ошибка обработки аудио: {e}")
                import traceback
                traceback.print_exc()
                return {"transcript": "", "word_count": 0}
            
        except Exception as e:
            print(f"⚠️  Ошибка транскрипции: {e}")
            import traceback
            traceback.print_exc()
            return {"transcript": "", "word_count": 0}
        finally:
            # Очистка временных файлов
            if tmp_video_path and os.path.exists(tmp_video_path):
                try:
                    os.unlink(tmp_video_path)
                except:
                    pass
            if tmp_audio_path and os.path.exists(tmp_audio_path):
                try:
                    os.unlink(tmp_audio_path)
                except:
                    pass
    
    def calculate_brainrot_index(self, embeddings: np.ndarray, patterns: List[Dict], 
                                transcript: Dict, video_duration: float) -> Dict:
        """Вычисляет BRAINROT INDEX на основе всех метрик"""
        
        # 1. Плотность резких переходов (вариация эмбеддингов)
        if len(embeddings) > 1:
            embedding_diffs = np.diff(embeddings, axis=0)
            transition_density = np.mean(np.linalg.norm(embedding_diffs, axis=1))
        else:
            transition_density = 0.0
        
        # 2. Количество "стимов" (высокая вариативность в паттернах)
        pattern_variability = len(set([str(p) for p in patterns])) / max(len(patterns), 1)
        
        # 3. Темп речи (слова в секунду)
        speech_rate = transcript.get("word_count", 0) / max(video_duration, 1)
        
        # 4. Мемные токены (простая эвристика)
        meme_keywords = ["мем", "кринж", "рофл", "вайб", "чилл", "бейс", "рип", "лол", "омг"]
        transcript_text = transcript.get("transcript", "").lower()
        meme_density = sum(1 for keyword in meme_keywords if keyword in transcript_text) / max(len(transcript_text.split()), 1)
        
        # 5. Гиперактивность (высокая частота смены кадров)
        hyperactivity = len(embeddings) / max(video_duration, 1)
        
        # Взвешенная метрика BRAINROT INDEX
        brainrot_index = (
            transition_density * 0.3 +
            pattern_variability * 0.2 +
            speech_rate * 0.2 +
            meme_density * 0.15 +
            hyperactivity * 0.15
        ) * 100  # Нормализуем до 0-100
        
        return {
            "brainrot_index": float(brainrot_index),
            "metrics": {
                "transition_density": float(transition_density),
                "pattern_variability": float(pattern_variability),
                "speech_rate": float(speech_rate),
                "meme_density": float(meme_density),
                "hyperactivity": float(hyperactivity)
            },
            "transcript": transcript.get("transcript", "")
        }
    
    async def analyze_video(self, video_url: str, video_duration: float = 30.0) -> Dict:
        """Полный анализ видео"""
        print(f"Анализ видео: {video_url}")
        
        try:
            # Скачиваем видео
            video_data = await self.download_video_stream(video_url)
            if not video_data:
                return {"error": "Не удалось загрузить видео"}
            
            # Извлекаем кадры
            print("Извлечение кадров...")
            frames = self.extract_frames(video_data, fps=1.0/WINDOW_SIZE_SECONDS)
            
            if not frames:
                return {"error": "Не удалось извлечь кадры"}
            
            # Получаем эмбеддинги
            print("Получение CLIP эмбеддингов...")
            embeddings = self.get_clip_embeddings(frames)
            
            # Классифицируем паттерны
            print("Классификация визуальных паттернов...")
            patterns = self.classify_visual_patterns(frames)
            
            # Транскрибируем аудио
            print("Транскрипция аудио...")
            transcript = self.transcribe_audio(video_data)
            
            # Вычисляем BRAINROT INDEX
            print("Вычисление BRAINROT INDEX...")
            result = self.calculate_brainrot_index(embeddings, patterns, transcript, video_duration)
            
            return result
        except Exception as e:
            print(f"Ошибка при анализе видео: {e}")
            return {"error": str(e)}

