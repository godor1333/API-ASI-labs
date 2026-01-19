import torch
import torch.nn as nn
import os
from typing import Dict
from sklearn.metrics import accuracy_score, f1_score
from models.base_model import BaseInferenceWrapper


# Архитектура модели
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 2)

    def forward(self, x):
        return self.fc(x)


class TorchInferenceModel(BaseInferenceWrapper[torch.Tensor]):
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TorchInferenceModel, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_path: str):
        if self._initialized:
            return
        super().__init__(model_path)
        self._initialized = True

    def _load_model(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Файл не найден: {path}")

        print(f"\n[LOAD] Загрузка модели из {path}...")

        # Загружаем данные из файла
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)

        # Если загружен OrderedDict (только веса), создаем модель и вставляем их
        if isinstance(checkpoint, dict):
            model = SimpleModel()
            model.load_state_dict(checkpoint)
        else:
            # Если загружен объект модели целиком
            model = checkpoint

        model.to(self.device)
        model.eval()
        return model

    def predict(self, data: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            if isinstance(data, torch.Tensor):
                data = data.to(self.device)
            return self.model(data)

    def get_metrics(self, y_true: list, y_pred: list) -> Dict[str, float]:
        # Вычисление метрик, специфичных для этой модели
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "f1": float(f1_score(y_true, y_pred, average='weighted'))
        }