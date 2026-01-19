from minatar import Environment
import numpy as np

class MinAtarWrapper:
    """Обертка для среды MinAtar"""
    
    def __init__(self, game_name="space_invaders"):
        self.env = Environment(game_name)
        self.game_name = game_name
        
    def reset(self):
        """Сброс среды"""
        self.env.reset()
        return self.env.state()
    
    def step(self, action):
        """Шаг в среде"""
        reward, terminated = self.env.act(action)
        next_state = self.env.state()
        return next_state, reward, terminated, {}
    
    def get_num_actions(self):
        """Количество доступных действий"""
        return self.env.num_actions()
    
    def get_state_shape(self):
        """Форма состояния"""
        return self.env.state_shape()
    
    def render(self):
        """Визуализация (опционально)"""
        return self.env.state()