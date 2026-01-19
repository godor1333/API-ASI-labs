import numpy as np
import random

class RandomAgent:
    """Случайный агент для тестирования"""
    
    def __init__(self, num_actions):
        self.num_actions = num_actions
    
    def get_action(self, state=None, step=None):
        """Случайное действие"""
        return random.randint(0, self.num_actions - 1)
    
    def update_q_values(self, state, action, reward, next_state):
        """Заглушка - случайный агент не обучается"""
        pass