import torch
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Dict

T = TypeVar('T')

class BaseInferenceWrapper(ABC, Generic[T]):
    def __init__(self, model_path: str):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Загрузка модели через абстрактный метод
        self.model = self._load_model(model_path)

    @abstractmethod
    def _load_model(self, path: str):
        pass

    @abstractmethod
    def predict(self, data: T) -> Any:
        pass

    @abstractmethod
    def get_metrics(self, y_true: list, y_pred: list) -> Dict[str, float]:
        pass