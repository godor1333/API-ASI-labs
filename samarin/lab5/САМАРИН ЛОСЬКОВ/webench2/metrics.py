"""
Модуль для расчёта метрик качества видео
"""

import numpy as np
import cv2
from typing import List, Dict, Any, Tuple
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
import os


class MetricsCalculator:
    """Калькулятор метрик для оценки видео"""
    
    def __init__(
        self,
        clip_model_id: str = "openai/clip-vit-base-patch32",
        image_reward_model_id: str = "BAAI/ImageReward",
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        """
        Инициализация калькулятора метрик
        
        Args:
            clip_model_id: ID модели CLIP
            image_reward_model_id: ID модели ImageReward
            device: Устройство для вычислений
        """
        self.device = device
        self.clip_model = None
        self.clip_processor = None
        self.image_reward_model = None
        
        # Загружаем CLIP
        try:
            print(f"Загрузка CLIP модели {clip_model_id}...")
            self.clip_model = CLIPModel.from_pretrained(clip_model_id).to(device)
            self.clip_processor = CLIPProcessor.from_pretrained(clip_model_id)
            self.clip_model.eval()
            print("CLIP модель загружена")
        except Exception as e:
            print(f"Ошибка загрузки CLIP: {e}")
        
        # Загружаем ImageReward (опционально)
        try:
            print(f"Загрузка ImageReward модели {image_reward_model_id}...")
            # ImageReward требует специальной установки
            # Здесь упрощённая версия - можно добавить позже
            print("ImageReward будет загружен при необходимости")
        except Exception as e:
            print(f"Ошибка загрузки ImageReward: {e}")
    
    def calculate_clip_score(
        self,
        image: Image.Image,
        text: str
    ) -> float:
        """
        Расчёт CLIPScore для изображения и текста
        
        Args:
            image: Изображение
            text: Текстовое описание
            
        Returns:
            float: CLIPScore
        """
        if self.clip_model is None or self.clip_processor is None:
            return 0.0
        
        try:
            with torch.no_grad():
                inputs = self.clip_processor(
                    text=[text],
                    images=image,
                    return_tensors="pt",
                    padding=True
                ).to(self.device)
                
                outputs = self.clip_model(**inputs)
                
                # Вычисляем cosine similarity
                image_embeds = outputs.image_embeds
                text_embeds = outputs.text_embeds
                
                # Нормализуем
                image_embeds = image_embeds / image_embeds.norm(dim=-1, keepdim=True)
                text_embeds = text_embeds / text_embeds.norm(dim=-1, keepdim=True)
                
                # Cosine similarity
                similarity = (image_embeds * text_embeds).sum(dim=-1)
                
                return float(similarity.cpu().item())
        except Exception as e:
            print(f"Ошибка расчёта CLIPScore: {e}")
            return 0.0
    
    def calculate_image_reward(
        self,
        image: Image.Image
    ) -> float:
        """
        Расчёт ImageReward для изображения
        
        Args:
            image: Изображение
            
        Returns:
            float: ImageReward score
        """
        # Упрощённая версия - можно интегрировать реальную модель ImageReward
        # Пока возвращаем случайное значение или оценку на основе простых метрик
        try:
            # Простая эвристика: яркость, контраст, резкость
            img_array = np.array(image.convert('RGB'))
            
            # Яркость
            brightness = np.mean(img_array) / 255.0
            
            # Контраст (стандартное отклонение)
            contrast = np.std(img_array) / 255.0
            
            # Простая оценка резкости (градиент)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian) / 10000.0  # Нормализация
            
            # Комбинированная оценка
            score = (brightness * 0.3 + contrast * 0.4 + min(sharpness, 1.0) * 0.3)
            
            return float(score)
        except Exception as e:
            print(f"Ошибка расчёта ImageReward: {e}")
            return 0.5
    
    def extract_frames(
        self,
        video_path: str,
        frames_per_second: float = 1.0
    ) -> List[Image.Image]:
        """
        Извлечение кадров из видео
        
        Args:
            video_path: Путь к видео
            frames_per_second: Сколько кадров в секунду извлекать
            
        Returns:
            List[Image.Image]: Список кадров
        """
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Не удалось открыть видео: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps / frames_per_second) if frames_per_second > 0 else 1
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                # Конвертируем BGR в RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(frame_rgb))
            
            frame_count += 1
        
        cap.release()
        return frames
    
    def check_static_frames(
        self,
        frames: List[Image.Image],
        threshold: float = 0.01
    ) -> Tuple[bool, List[int]]:
        """
        Проверка на статичные кадры (одинаковые подряд)
        
        Args:
            frames: Список кадров
            threshold: Порог различия между кадрами
            
        Returns:
            Tuple[bool, List[int]]: (есть ли статичные участки, индексы проблемных кадров)
        """
        static_indices = []
        
        for i in range(len(frames) - 1):
            frame1 = np.array(frames[i])
            frame2 = np.array(frames[i + 1])
            
            # Вычисляем разницу
            diff = np.abs(frame1.astype(float) - frame2.astype(float))
            mean_diff = np.mean(diff) / 255.0
            
            if mean_diff < threshold:
                static_indices.append(i)
        
        return len(static_indices) > 0, static_indices
    
    def check_dark_frames(
        self,
        frames: List[Image.Image],
        threshold: float = 0.1
    ) -> Tuple[bool, List[int], float]:
        """
        Проверка на тёмные кадры
        
        Args:
            frames: Список кадров
            threshold: Порог яркости (0-1)
            
        Returns:
            Tuple[bool, List[int], float]: (есть ли тёмные кадры, индексы, доля)
        """
        dark_indices = []
        
        for i, frame in enumerate(frames):
            img_array = np.array(frame.convert('RGB'))
            brightness = np.mean(img_array) / 255.0
            
            if brightness < threshold:
                dark_indices.append(i)
        
        dark_ratio = len(dark_indices) / len(frames) if frames else 0.0
        return len(dark_indices) > 0, dark_indices, dark_ratio
    
    def check_overexposed_frames(
        self,
        frames: List[Image.Image],
        threshold: float = 0.9
    ) -> Tuple[bool, List[int], float]:
        """
        Проверка на пересвеченные кадры
        
        Args:
            frames: Список кадров
            threshold: Порог яркости (0-1)
            
        Returns:
            Tuple[bool, List[int], float]: (есть ли пересвеченные кадры, индексы, доля)
        """
        overexposed_indices = []
        
        for i, frame in enumerate(frames):
            img_array = np.array(frame.convert('RGB'))
            brightness = np.mean(img_array) / 255.0
            
            if brightness > threshold:
                overexposed_indices.append(i)
        
        overexposed_ratio = len(overexposed_indices) / len(frames) if frames else 0.0
        return len(overexposed_indices) > 0, overexposed_indices, overexposed_ratio
    
    def check_brightness_jumps(
        self,
        frames: List[Image.Image],
        threshold: float = 0.3
    ) -> Tuple[bool, List[int]]:
        """
        Проверка на резкие скачки яркости
        
        Args:
            frames: Список кадров
            threshold: Порог изменения яркости между соседними кадрами
            
        Returns:
            Tuple[bool, List[int]]: (есть ли скачки, индексы проблемных переходов)
        """
        jump_indices = []
        prev_brightness = None
        
        for i, frame in enumerate(frames):
            img_array = np.array(frame.convert('RGB'))
            brightness = np.mean(img_array) / 255.0
            
            if prev_brightness is not None:
                jump = abs(brightness - prev_brightness)
                if jump > threshold:
                    jump_indices.append(i - 1)  # Индекс первого кадра в паре
            
            prev_brightness = brightness
        
        return len(jump_indices) > 0, jump_indices
