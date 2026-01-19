"""
Основной модуль оценки видео через Webench2
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np

from .metrics import MetricsCalculator


class Webench2Evaluator:
    """Оценщик видео через Webench2"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация оценщика
        
        Args:
            config_path: Путь к конфигурационному файлу
        """
        self.config = self._load_config(config_path)
        
        webench2_config = self.config.get("webench2", {})
        metrics_config = webench2_config.get("metrics", {})
        
        clip_model_id = metrics_config.get("clip_score", {}).get("model", "openai/clip-vit-base-patch32")
        
        self.metrics_calculator = MetricsCalculator(clip_model_id=clip_model_id)
        
        self.frame_sampling_config = webench2_config.get("frame_sampling", {})
        self.metrics_config = metrics_config
        
        # Директория для результатов
        self.results_dir = self.config.get("paths", {}).get("results", "results")
        os.makedirs(self.results_dir, exist_ok=True)
    
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
    
    def evaluate_video(
        self,
        video_path: str,
        prompt_text: str,
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Оценка видео по всем метрикам Webench2
        
        Args:
            video_path: Путь к видео
            prompt_text: Текстовое описание
            save_results: Сохранять ли результаты в файл
            
        Returns:
            dict: Словарь с метриками
        """
        print(f"Оценка видео: {video_path}")
        print(f"Промпт: {prompt_text}")
        
        # Извлекаем кадры
        frames_per_second = self.frame_sampling_config.get("frames_per_second", 1.0)
        frames = self.metrics_calculator.extract_frames(video_path, frames_per_second)
        
        if not frames:
            raise ValueError(f"Не удалось извлечь кадры из видео: {video_path}")
        
        print(f"Извлечено кадров: {len(frames)}")
        
        # Вычисляем метрики
        metrics = {}
        
        # CLIPScore по кадрам
        if self.metrics_config.get("clip_score", {}).get("enabled", True):
            print("Вычисление CLIPScore...")
            clip_scores = []
            for i, frame in enumerate(frames):
                score = self.metrics_calculator.calculate_clip_score(frame, prompt_text)
                clip_scores.append(score)
                if (i + 1) % 10 == 0:
                    print(f"  Обработано кадров: {i+1}/{len(frames)}")
            
            metrics["clip_score"] = {
                "scores": clip_scores,
                "mean": float(np.mean(clip_scores)),
                "min": float(np.min(clip_scores)),
                "max": float(np.max(clip_scores)),
                "std": float(np.std(clip_scores)),  # Дисперсия/стабильность
                "variance": float(np.var(clip_scores))
            }
        
        # ImageReward по выборке кадров
        if self.metrics_config.get("image_reward", {}).get("enabled", True):
            print("Вычисление ImageReward...")
            sample_rate = self.metrics_config.get("image_reward", {}).get("sample_rate", 0.5)
            num_samples = max(1, int(len(frames) * sample_rate))
            sample_indices = np.linspace(0, len(frames) - 1, num_samples, dtype=int)
            
            image_rewards = []
            for idx in sample_indices:
                score = self.metrics_calculator.calculate_image_reward(frames[idx])
                image_rewards.append(score)
            
            metrics["image_reward"] = {
                "scores": image_rewards,
                "mean": float(np.mean(image_rewards)),
                "min": float(np.min(image_rewards)),
                "max": float(np.max(image_rewards)),
                "std": float(np.std(image_rewards))
            }
        
        # Технические проверки
        stability_config = self.metrics_config.get("stability", {})
        
        if stability_config.get("check_duplicates", True):
            print("Проверка на статичные кадры...")
            has_static, static_indices = self.metrics_calculator.check_static_frames(frames)
            metrics["static_frames"] = {
                "has_static": has_static,
                "indices": static_indices,
                "count": len(static_indices),
                "ratio": len(static_indices) / len(frames) if frames else 0.0
            }
        
        if stability_config.get("check_dark_frames", True):
            print("Проверка на тёмные кадры...")
            threshold = stability_config.get("brightness_threshold", 0.1)
            has_dark, dark_indices, dark_ratio = self.metrics_calculator.check_dark_frames(frames, threshold)
            metrics["dark_frames"] = {
                "has_dark": has_dark,
                "indices": dark_indices,
                "count": len(dark_indices),
                "ratio": dark_ratio
            }
        
        if stability_config.get("check_overexposed", True):
            print("Проверка на пересвеченные кадры...")
            threshold = stability_config.get("overexposure_threshold", 0.9)
            has_overexposed, overexposed_indices, overexposed_ratio = self.metrics_calculator.check_overexposed_frames(frames, threshold)
            metrics["overexposed_frames"] = {
                "has_overexposed": has_overexposed,
                "indices": overexposed_indices,
                "count": len(overexposed_indices),
                "ratio": overexposed_ratio
            }
        
        # Проверка скачков яркости
        print("Проверка скачков яркости...")
        has_jumps, jump_indices = self.metrics_calculator.check_brightness_jumps(frames)
        metrics["brightness_jumps"] = {
            "has_jumps": has_jumps,
            "indices": jump_indices,
            "count": len(jump_indices)
        }
        
        # Сводный индекс качества
        metrics["quality_index"] = self._calculate_quality_index(metrics)
        
        # Добавляем метаданные
        metrics["metadata"] = {
            "video_path": video_path,
            "prompt": prompt_text,
            "num_frames": len(frames),
            "frames_per_second": frames_per_second
        }
        
        # Сохраняем результаты
        if save_results:
            self._save_results(metrics, video_path)
        
        return metrics
    
    def _calculate_quality_index(self, metrics: Dict[str, Any]) -> float:
        """
        Вычисление сводного индекса качества
        
        Args:
            metrics: Словарь с метриками
            
        Returns:
            float: Индекс качества (0-1)
        """
        score = 1.0
        
        # Штрафы за проблемы
        if "static_frames" in metrics:
            score -= metrics["static_frames"]["ratio"] * 0.3
        
        if "dark_frames" in metrics:
            score -= metrics["dark_frames"]["ratio"] * 0.2
        
        if "overexposed_frames" in metrics:
            score -= metrics["overexposed_frames"]["ratio"] * 0.2
        
        if "brightness_jumps" in metrics:
            score -= min(metrics["brightness_jumps"]["count"] / 10.0, 0.2)
        
        # Бонусы за хорошие метрики
        if "clip_score" in metrics:
            # Нормализуем CLIPScore (обычно в диапазоне 0-1, но может быть больше)
            clip_mean = metrics["clip_score"]["mean"]
            clip_contribution = min(clip_mean / 0.5, 1.0) * 0.3
            score = score * 0.7 + clip_contribution
        
        if "image_reward" in metrics:
            image_reward_mean = metrics["image_reward"]["mean"]
            score = score * 0.8 + image_reward_mean * 0.2
        
        # Штраф за высокую дисперсию CLIPScore (нестабильность)
        if "clip_score" in metrics:
            clip_std = metrics["clip_score"]["std"]
            stability_penalty = min(clip_std / 0.2, 0.3)
            score -= stability_penalty
        
        return max(0.0, min(1.0, score))
    
    def _save_results(self, metrics: Dict[str, Any], video_path: str):
        """
        Сохранение результатов в файл
        
        Args:
            metrics: Словарь с метриками
            video_path: Путь к видео
        """
        video_name = Path(video_path).stem
        results_file = os.path.join(self.results_dir, f"{video_name}_metrics.json")
        
        # Удаляем массивы scores для компактности (можно оставить если нужно)
        metrics_to_save = metrics.copy()
        if "clip_score" in metrics_to_save:
            metrics_to_save["clip_score"] = {k: v for k, v in metrics_to_save["clip_score"].items() if k != "scores"}
        if "image_reward" in metrics_to_save:
            metrics_to_save["image_reward"] = {k: v for k, v in metrics_to_save["image_reward"].items() if k != "scores"}
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(metrics_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"Результаты сохранены: {results_file}")
