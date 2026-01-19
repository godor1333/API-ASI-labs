# object_detection/detector_factory.py
from .simple_detector import SimpleObjectDetector
from .detr_detector import DETRDetector
import torch

class DetectorFactory:
    """Фабрика для создания детекторов"""
    
    @staticmethod
    def create_detector(detector_type="simple", use_gpu=False):
        """
        Создает детектор указанного типа
        
        Args:
            detector_type: "simple", "detr", или "auto" (автовыбор)
            use_gpu: использовать ли GPU если доступно
        """
        device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        
        if detector_type == "simple":
            print("🔍 Используется простой детектор")
            return SimpleObjectDetector()
        
        elif detector_type == "detr":
            try:
                print(f"🔍 Загружаем DETR на {device}...")
                return DETRDetector(device=device)
            except Exception as e:
                print(f"⚠️ Не удалось загрузить DETR: {e}")
                print("🔄 Возвращаемся к простому детектору")
                return SimpleObjectDetector()
        
        elif detector_type == "auto":
            # Автоматически выбираем лучший доступный
            try:
                # Проверяем, можем ли загрузить DETR
                detector = DETRDetector(device=device)
                print(f"✅ Автовыбор: DETR на {device}")
                return detector
            except:
                print("⚠️ Автовыбор: простой детектор (DETR недоступен)")
                return SimpleObjectDetector()
        
        else:
            print(f"⚠️ Неизвестный тип детектора: {detector_type}")
            return SimpleObjectDetector()