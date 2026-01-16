import pytest
import torch
import os
import __main__
from models.model_loader import SimpleModel, TorchInferenceModel

# Регистрируем класс в __main__ для корректной работы torch.load
setattr(__main__, "SimpleModel", SimpleModel)

@pytest.fixture(scope="session")
def global_model():
    """Загружает модель один раз на всю сессию тестов"""
    model_path = os.path.join("models", "prod_model.pt")
    return TorchInferenceModel(model_path)

@pytest.fixture(scope="session")
def test_dataset():
    """Спарсенные тестовые данные"""
    return [
        {"input": torch.randn(1, 10), "label": 1},
        {"input": torch.randn(1, 10), "label": 0},
        {"input": torch.randn(1, 10), "label": 1},
        {"input": torch.randn(1, 10), "label": 0},
        {"input": torch.randn(1, 10), "label": 1}
    ]