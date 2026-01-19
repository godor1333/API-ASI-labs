import numpy as np
import pytest
from tests.model_registry import ModelRegistry


@pytest.mark.parametrize("iteration", range(5))
def test_model_stability(iteration):
    """Проверка, что точность/результат не меняется от запуска к запуску"""
    classifier = ModelRegistry.get_model("classifier")

    # Фиксированный вход (белый квадрат)
    test_frame = np.ones((128, 128, 3), dtype=np.uint8) * 255

    result = classifier.classify(test_frame)

    # Сохраняем результат первого запуска для сравнения
    if iteration == 0:
        test_model_stability.first_result = result

    assert result == test_model_stability.first_result, f"Результат изменился на итерации {iteration}"


def test_parser_step():
    """Автотест шага парсинга: проверка формата выходных данных"""
    detector = ModelRegistry.get_model("detector")
    test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    detections = detector.analyze_frame(test_frame)

    assert isinstance(detections, list), "Результат детектора должен быть списком"
    if len(detections) > 0:
        assert "label" in detections[0], "Парсер не вернул метку объекта"