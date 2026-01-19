"""
Генератор ключевых кадров для видео
"""

import os
from typing import List, Optional
from PIL import Image
import torch
import numpy as np

# Импортируем SDXL только если нужно
try:
    from diffusers import StableDiffusionXLPipeline
    SDXL_AVAILABLE = True
except ImportError:
    SDXL_AVAILABLE = False


class KeyframeGenerator:
    """Генератор ключевых кадров через SDXL или использование предопределённых"""
    
    def __init__(
        self,
        model_id: str = "stabilityai/sdxl-turbo",
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        use_sdxl: bool = True
    ):
        """
        Инициализация генератора ключевых кадров
        
        Args:
            model_id: ID модели SDXL
            device: Устройство для вычислений
            use_sdxl: Использовать ли SDXL для генерации
        """
        self.model_id = model_id
        self.device = device
        self.use_sdxl = use_sdxl
        self.pipeline = None
        
        if use_sdxl:
            # Проверяем переменную окружения для предотвращения автоматической загрузки
            if os.getenv("DISABLE_SDXL_AUTO_LOAD", "false").lower() == "true":
                print("Автоматическая загрузка SDXL отключена (DISABLE_SDXL_AUTO_LOAD=true)")
                print("Используется режим stub-кадров")
                self.use_sdxl = False
            else:
                if not SDXL_AVAILABLE:
                    print("diffusers не установлен или SDXL недоступен")
                    print("Используется режим stub-кадров")
                    self.use_sdxl = False
                else:
                    try:
                        print(f"Загрузка модели {model_id}...")
                        print("⚠️  ВНИМАНИЕ: Это загрузит ~10+ ГБ моделей!")
                        print("   Для использования stub-кадров установите DISABLE_SDXL_AUTO_LOAD=true")
                        print("   или измените config.yaml: generation.keyframe_generation.method = 'stub'")
                        
                        response = input("Продолжить загрузку? (y/n): ").strip().lower()
                        if response != 'y':
                            print("Загрузка отменена. Используется режим stub-кадров")
                            self.use_sdxl = False
                            return
                        
                        self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                            model_id,
                            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
                            variant="fp16" if device == "cuda" else None
                        )
                        self.pipeline = self.pipeline.to(device)
                        if device == "cuda":
                            self.pipeline.enable_model_cpu_offload()
                        print("Модель загружена")
                    except KeyboardInterrupt:
                        print("\nЗагрузка прервана пользователем. Используется режим stub-кадров")
                        self.use_sdxl = False
                    except Exception as e:
                        print(f"Ошибка загрузки модели: {e}")
                        print("Будет использован режим stub-кадров")
                        self.use_sdxl = False
    
    def generate_keyframe(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        num_inference_steps: int = 4,
        guidance_scale: float = 0.0,
        width: int = 1024,
        height: int = 576
    ) -> Image.Image:
        """
        Генерация одного ключевого кадра
        
        Args:
            prompt: Текстовое описание
            negative_prompt: Негативный промпт
            num_inference_steps: Количество шагов
            guidance_scale: Guidance scale
            width: Ширина изображения
            height: Высота изображения
            
        Returns:
            PIL.Image: Сгенерированное изображение
        """
        if not self.use_sdxl or self.pipeline is None:
            # Генерируем stub-кадр (однотонное изображение)
            return self._generate_stub_image(width, height)
        
        try:
            image = self.pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                width=width,
                height=height
            ).images[0]
            return image
        except Exception as e:
            print(f"Ошибка генерации кадра: {e}")
            return self._generate_stub_image(width, height)
    
    def generate_keyframes_from_scenes(
        self,
        scene_descriptions: List[str],
        num_keyframes: Optional[int] = None,
        **kwargs
    ) -> List[Image.Image]:
        """
        Генерация ключевых кадров из описаний сцен
        
        Args:
            scene_descriptions: Список описаний сцен
            num_keyframes: Количество ключевых кадров (если None, используется длина списка)
            **kwargs: Дополнительные параметры для генерации
            
        Returns:
            List[PIL.Image]: Список ключевых кадров
        """
        if num_keyframes is None:
            num_keyframes = len(scene_descriptions)
        
        keyframes = []
        for i, description in enumerate(scene_descriptions[:num_keyframes]):
            print(f"Генерация ключевого кадра {i+1}/{num_keyframes}: {description[:50]}...")
            keyframe = self.generate_keyframe(description, **kwargs)
            keyframes.append(keyframe)
        
        return keyframes
    
    def _generate_stub_image(self, width: int, height: int) -> Image.Image:
        """
        Генерация stub-изображения (заглушка)
        
        Args:
            width: Ширина
            height: Высота
            
        Returns:
            PIL.Image: Stub-изображение
        """
        # Создаём простое градиентное изображение
        array = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            intensity = int(255 * (y / height))
            array[y, :] = [intensity // 3, intensity // 2, intensity]
        
        return Image.fromarray(array)
    
    def save_keyframes(self, keyframes: List[Image.Image], output_dir: str, prefix: str = "keyframe"):
        """
        Сохранение ключевых кадров
        
        Args:
            keyframes: Список изображений
            output_dir: Директория для сохранения
            prefix: Префикс имени файла
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for i, keyframe in enumerate(keyframes):
            filename = f"{prefix}_{i:03d}.png"
            filepath = os.path.join(output_dir, filename)
            keyframe.save(filepath)
            print(f"Сохранён ключевой кадр: {filepath}")
