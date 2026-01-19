"""
Основной модуль генерации видео из текстового описания
"""

import os
import json
from typing import List, Optional, Dict, Any
from PIL import Image
import numpy as np
import cv2
from pathlib import Path

from .keyframe_generator import KeyframeGenerator
from .comfyui_client import ComfyUIClient


class VideoGenerator:
    """Генератор видео из текстового описания"""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        comfyui_host: str = "localhost",
        comfyui_port: int = 8188
    ):
        """
        Инициализация генератора видео
        
        Args:
            config_path: Путь к конфигурационному файлу
            comfyui_host: Хост ComfyUI
            comfyui_port: Порт ComfyUI
        """
        self.config = self._load_config(config_path)
        self.comfyui_client = ComfyUIClient(host=comfyui_host, port=comfyui_port)
        
        # Определяем, использовать ли SDXL на основе конфига
        keyframe_method = self.config.get("generation", {}).get("keyframe_generation", {}).get("method", "stub")
        use_sdxl = (keyframe_method == "sdxl")
        
        self.keyframe_generator = KeyframeGenerator(
            model_id=self.config.get("models", {}).get("sdxl", {}).get("model_id", "stabilityai/sdxl-turbo"),
            use_sdxl=use_sdxl
        )
        
        # Создаём директории для выходных файлов
        self.output_dir = self.config.get("paths", {}).get("outputs", "outputs")
        self.keyframes_dir = self.config.get("paths", {}).get("keyframes", "outputs/keyframes")
        self.videos_dir = self.config.get("paths", {}).get("videos", "outputs/videos")
        
        os.makedirs(self.keyframes_dir, exist_ok=True)
        os.makedirs(self.videos_dir, exist_ok=True)
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
        
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}, используются значения по умолчанию")
            return {}
    
    def parse_scenes(self, text_description: str) -> List[str]:
        """
        Парсинг текстового описания на отдельные сцены
        
        Args:
            text_description: Текстовое описание
            
        Returns:
            List[str]: Список описаний сцен
        """
        # Простой парсинг: разделяем по запятым или точкам
        # В реальности можно использовать более сложную логику
        scenes = []
        
        # Разделяем по запятым, точкам с запятой или точкам
        separators = [',', ';', '.']
        current_scene = ""
        
        for char in text_description:
            if char in separators and current_scene.strip():
                scenes.append(current_scene.strip())
                current_scene = ""
            else:
                current_scene += char
        
        if current_scene.strip():
            scenes.append(current_scene.strip())
        
        # Если не удалось разделить, возвращаем весь текст как одну сцену
        if not scenes:
            scenes = [text_description]
        
        return scenes
    
    def generate_from_text(
        self,
        text_description: str,
        output_filename: Optional[str] = None,
        num_keyframes: Optional[int] = None
    ) -> str:
        """
        Генерация видео из текстового описания
        
        Args:
            text_description: Текстовое описание сцен
            output_filename: Имя выходного файла (если None, генерируется автоматически)
            num_keyframes: Количество ключевых кадров
            
        Returns:
            str: Путь к сгенерированному видео
        """
        print(f"Генерация видео для описания: {text_description}")
        
        # Парсим описание на сцены
        scenes = self.parse_scenes(text_description)
        print(f"Распознано сцен: {len(scenes)}")
        
        # Определяем количество ключевых кадров
        if num_keyframes is None:
            num_keyframes = self.config.get("generation", {}).get("keyframe_generation", {}).get("num_keyframes", 3)
        
        # Генерируем ключевые кадры
        keyframes = self.keyframe_generator.generate_keyframes_from_scenes(
            scenes,
            num_keyframes=num_keyframes
        )
        
        # Сохраняем ключевые кадры
        session_id = f"session_{len(os.listdir(self.keyframes_dir))}"
        keyframe_dir = os.path.join(self.keyframes_dir, session_id)
        self.keyframe_generator.save_keyframes(keyframes, keyframe_dir)
        
        # Генерируем клипы для каждого ключевого кадра
        clips = []
        clip_duration = self.config.get("generation", {}).get("clip_duration", 2.0)
        fps = self.config.get("generation", {}).get("fps", 24)
        
        for i, keyframe in enumerate(keyframes):
            print(f"Генерация клипа {i+1}/{len(keyframes)}...")
            clip = self._generate_clip_from_keyframe(keyframe, clip_duration, fps)
            if clip is not None:
                clips.append(clip)
        
        # Склеиваем клипы в один ролик
        if not clips:
            raise ValueError("Не удалось сгенерировать ни одного клипа")
        
        video = self._concatenate_clips(clips, fps)
        
        # Сохраняем видео
        if output_filename is None:
            import time
            output_filename = f"video_{int(time.time())}.mp4"
        
        output_path = os.path.join(self.videos_dir, output_filename)
        self._save_video(video, output_path, fps)
        
        print(f"Видео сохранено: {output_path}")
        return output_path
    
    def _generate_clip_from_keyframe(
        self,
        keyframe: Image.Image,
        duration: float,
        fps: int
    ) -> Optional[np.ndarray]:
        """
        Генерация клипа из ключевого кадра через SVD
        
        Args:
            keyframe: Ключевой кадр
            duration: Длительность клипа в секундах
            fps: FPS
            
        Returns:
            np.ndarray: Массив кадров (N, H, W, 3) или None при ошибке
        """
        # Сохраняем ключевой кадр во временный файл
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            keyframe.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Проверяем подключение к ComfyUI
            if not self.comfyui_client.is_connected:
                self.comfyui_client.connect()
            
            if not self.comfyui_client.is_connected:
                print("ComfyUI не подключен, используем stub-режим")
                raise ValueError("ComfyUI не доступен")
            
            # Параметры SVD из конфига
            svd_config = self.config.get("models", {}).get("svd", {})
            num_frames = int(duration * fps)
            num_inference_steps = svd_config.get("num_inference_steps", 50)
            guidance_scale = svd_config.get("guidance_scale", 7.5)
            
            # Генерируем через ComfyUI
            workflow = self.comfyui_client.generate_svd_workflow(
                image_path=temp_path,
                num_frames=num_frames,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
            
            prompt_id = self.comfyui_client.queue_prompt(workflow)
            results = self.comfyui_client.wait_for_completion(prompt_id)
            
            # Получаем сгенерированные кадры
            # Примечание: реальная реализация зависит от структуры ответа ComfyUI
            # Здесь упрощённая версия - возвращаем статичный кадр, повторённый N раз
            frames = []
            keyframe_array = np.array(keyframe)
            
            for _ in range(num_frames):
                frames.append(keyframe_array)
            
            return np.array(frames)
            
        except ValueError as e:
            # Ошибки связанные с отсутствием нод или подключением
            error_msg = str(e)
            if "does not exist" in error_msg or "Нода не найдена" in error_msg:
                print(f"⚠️  {error_msg}")
                print("   Используется stub-режим (статичные кадры)")
            else:
                print(f"⚠️  {error_msg}")
                print("   Используется stub-режим")
            # Возвращаем статичный клип как fallback
            keyframe_array = np.array(keyframe)
            num_frames = int(duration * fps)
            return np.array([keyframe_array] * num_frames)
        except Exception as e:
            print(f"⚠️  Ошибка генерации клипа через ComfyUI: {e}")
            print("   Используется stub-режим (статичные кадры)")
            # Возвращаем статичный клип как fallback
            keyframe_array = np.array(keyframe)
            num_frames = int(duration * fps)
            return np.array([keyframe_array] * num_frames)
        
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _concatenate_clips(self, clips: List[np.ndarray], fps: int) -> np.ndarray:
        """
        Склейка клипов в один ролик
        
        Args:
            clips: Список массивов кадров
            fps: FPS
            
        Returns:
            np.ndarray: Объединённый массив кадров
        """
        if not clips:
            raise ValueError("Список клипов пуст")
        
        # Проверяем размеры и приводим к одному
        target_height = clips[0].shape[1]
        target_width = clips[0].shape[2]
        
        normalized_clips = []
        for clip in clips:
            if clip.shape[1] != target_height or clip.shape[2] != target_width:
                # Ресайзим
                resized_frames = []
                for frame in clip:
                    frame_img = Image.fromarray(frame)
                    frame_img = frame_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    resized_frames.append(np.array(frame_img))
                clip = np.array(resized_frames)
            normalized_clips.append(clip)
        
        # Объединяем все кадры
        video = np.concatenate(normalized_clips, axis=0)
        return video
    
    def _save_video(self, video: np.ndarray, output_path: str, fps: int):
        """
        Сохранение видео в файл
        
        Args:
            video: Массив кадров (N, H, W, 3)
            output_path: Путь для сохранения
            fps: FPS
        """
        # Конвертируем RGB в BGR для OpenCV
        video_bgr = video[..., ::-1]
        
        # Получаем размеры
        height, width = video_bgr.shape[1:3]
        
        # Создаём VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        for frame in video_bgr:
            out.write(frame)
        
        out.release()
        print(f"Видео сохранено: {output_path}")
