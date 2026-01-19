# tests/test_integration.py
import unittest
import numpy as np
from env_wrapper.minatar_wrapper import MinAtarWrapper
from object_detection.simple_detector import SimpleObjectDetector
from agents.epsilon_greedy import EpsilonGreedyAgent

class TestIntegration(unittest.TestCase):
    def test_full_pipeline(self):
        """Тест полного пайплайна: среда → детектор → агент"""
        # 1. Инициализация
        env = MinAtarWrapper("space_invaders")
        detector = SimpleObjectDetector()
        agent = EpsilonGreedyAgent(env.get_num_actions())
        
        # 2. Один шаг
        state = env.reset()
        objects = detector.detect(state)
        action = agent.get_action(state)
        next_state, reward, terminated, _ = env.step(action)
        
        # Проверки
        self.assertIsInstance(objects, list, "Детектор должен возвращать список")
        self.assertIn(action, range(env.get_num_actions()), 
                     "Действие должно быть валидным")
        
        # Исправлено: проверка на числовой тип (включая numpy)
        self.assertTrue(isinstance(reward, (int, float, np.integer, np.floating)),
                       f"Награда должна быть числом, получено {type(reward)}")
        
        self.assertIsInstance(terminated, bool, "Флаг terminated должен быть bool")
        
        print("✅ Полный пайплайн работает корректно")