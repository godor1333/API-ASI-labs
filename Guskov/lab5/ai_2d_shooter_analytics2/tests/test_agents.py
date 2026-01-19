# tests/test_agents.py
import unittest
import numpy as np
from agents.random_agent import RandomAgent
from agents.epsilon_greedy import EpsilonGreedyAgent

class TestAgents(unittest.TestCase):
    def test_random_agent_actions(self):
        """Тест: случайный агент возвращает допустимые действия"""
        agent = RandomAgent(num_actions=6)
        state = np.random.rand(10, 10, 6)
        
        for _ in range(100):
            action = agent.get_action(state)
            self.assertIn(action, range(6), 
                         f"Действие {action} вне диапазона 0-5")
    
    def test_epsilon_greedy_q_table(self):
        """Тест: ε-greedy агент обновляет Q-таблицу"""
        agent = EpsilonGreedyAgent(num_actions=6, epsilon=0.1)
        state = np.ones((10, 10, 6))
        next_state = np.zeros((10, 10, 6))
        
        # Проверяем обновление Q-значений
        old_q_size = len(agent.q_table)
        agent.update_q_values(state, action=0, reward=1.0, next_state=next_state)
        new_q_size = len(agent.q_table)
        
        self.assertGreater(new_q_size, old_q_size,
                          "Q-таблица должна увеличиться после обновления")
    
    def test_agent_action_range(self):
        """Тест: все агенты возвращают валидные действия"""
        agents = [
            ("random", RandomAgent(6)),
            ("epsilon_greedy", EpsilonGreedyAgent(6))
        ]
        
        test_state = np.random.rand(10, 10, 6)
        
        for name, agent in agents:
            for _ in range(10):
                action = agent.get_action(test_state)
                self.assertIn(action, range(6),
                             f"Агент {name}: действие {action} вне диапазона")