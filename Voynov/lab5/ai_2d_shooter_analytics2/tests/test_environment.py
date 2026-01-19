# tests/test_environment.py
import unittest
import numpy as np
from env_wrapper.minatar_wrapper import MinAtarWrapper

class TestEnvironment(unittest.TestCase):
    def test_env_reset(self):
        """Тест: сброс среды возвращает состояние"""
        env = MinAtarWrapper("space_invaders")
        state = env.reset()
        
        self.assertIsInstance(state, np.ndarray, 
                            "Состояние должно быть numpy массивом")
        self.assertEqual(state.shape, (10, 10, 6),
                        f"Неверная форма состояния: {state.shape}")
    
    def test_env_step(self):
        """Тест: шаг в среде возвращает корректные данные"""
        env = MinAtarWrapper("space_invaders")
        env.reset()
        
        # Тестируем все действия
        for action in range(env.get_num_actions()):
            next_state, reward, terminated, info = env.step(action)
            
            self.assertIsInstance(next_state, np.ndarray,
                                "Следующее состояние должно быть numpy массивом")
            
            # Исправлено: np.int64 тоже считается числом
            self.assertTrue(isinstance(reward, (int, float, np.integer, np.floating)),
                          f"Награда должна быть числом, получено {type(reward)}: {reward}")
            
            self.assertIsInstance(terminated, bool,
                                "Флаг terminated должен быть bool")
    
    def test_num_actions(self):
        """Тест: количество действий корректно"""
        env = MinAtarWrapper("space_invaders")
        num_actions = env.get_num_actions()
        
        self.assertEqual(num_actions, 6, 
                        f"Space Invaders должно иметь 6 действий, получено {num_actions}")