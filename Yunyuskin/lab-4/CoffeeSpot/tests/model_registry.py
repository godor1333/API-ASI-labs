import torch
from analysis.classifier import SituationClassifier
from analysis.detector import MazeDetector
from analysis.text_analyser import LoopDetector

class ModelRegistry:
    """Дженерик-класс (Registry) для управления моделями без повторной загрузки."""
    _instances = {}

    @classmethod
    def get_model(cls, model_key):
        if model_key not in cls._instances:
            print(f"\n[Registry] Единоразовая загрузка: {model_key}")
            if model_key == "classifier":
                cls._instances[model_key] = SituationClassifier()
            elif model_key == "detector":
                cls._instances[model_key] = MazeDetector()
            elif model_key == "loop_detector":
                cls._instances[model_key] = LoopDetector()
        return cls._instances[model_key]