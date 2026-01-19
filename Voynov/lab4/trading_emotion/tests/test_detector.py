# tests/test_detector.py
import unittest
import numpy as np
from object_detection.simple_detector import SimpleObjectDetector

class TestDetector(unittest.TestCase):
    def setUp(self):
        self.detector = SimpleObjectDetector()
        # Создаем тестовое состояние MinAtar
        self.test_state = np.zeros((10, 10, 6))
        # Добавляем "игрока" в канале 2
        self.test_state[5, 5, 2] = 1.0
        # Добавляем "врага" в канале 0
        self.test_state[2, 2, 0] = 1.0
    
    def test_detection_returns_list(self):
        """Тест: детектор возвращает список объектов"""
        objects = self.detector.detect(self.test_state)
        self.assertIsInstance(objects, list, 
                            "Детектор должен возвращать список")
    
    def test_detection_consistency(self):
        """Тест: детектор возвращает одинаковые результаты для одного состояния"""
        results = []
        for _ in range(5):
            objects = self.detector.detect(self.test_state)
            results.append(len(objects))
        
        # Все результаты должны быть одинаковыми
        self.assertTrue(all(r == results[0] for r in results),
                       f"Несогласованные результаты: {results}")
    
    def test_object_structure(self):
        """Тест: структура объектов корректна"""
        objects = self.detector.detect(self.test_state)
        
        if objects:  # Если что-то обнаружено
            obj = objects[0]
            required_keys = ['type', 'position', 'bbox', 'confidence']
            
            for key in required_keys:
                self.assertIn(key, obj,
                            f"Объект должен содержать ключ '{key}'")