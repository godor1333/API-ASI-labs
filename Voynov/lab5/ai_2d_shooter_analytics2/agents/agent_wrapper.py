import time
from utils.model_interface import ModelInterface

class AgentWrapper(ModelInterface):
    """Обертка для RL агентов под generic интерфейс"""
    
    def __init__(self, agent, agent_name):
        super().__init__(f"agent_{agent_name}")
        self.agent = agent
        self.agent_name = agent_name
    
    def predict(self, state):
        """Предсказание действия"""
        start_time = time.time()
        
        # Для разных типов агентов
        if hasattr(self.agent, 'get_action'):
            # Пробуем разные сигнатуры метода
            try:
                action = self.agent.get_action(state, step=0, training=False)
            except:
                try:
                    action = self.agent.get_action(state, step=0)
                except:
                    action = self.agent.get_action(state)
        elif hasattr(self.agent, 'act'):
            action = self.agent.act(state)
        elif hasattr(self.agent, 'predict'):
            action = self.agent.predict(state)
        else:
            # Fallback для случайного агента
            import random
            if hasattr(self.agent, 'num_actions'):
                action = random.randint(0, self.agent.num_actions - 1)
            else:
                action = 0
        
        inference_time = time.time() - start_time
        self.inference_times.append(inference_time)
        self.total_inferences += 1
        
        return {
            'action': action,
            'inference_time_ms': inference_time * 1000,
            'agent_type': self.agent_name
        }