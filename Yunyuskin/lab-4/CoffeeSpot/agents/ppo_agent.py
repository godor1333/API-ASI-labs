from stable_baselines3 import PPO

class MazeAgent:
    def __init__(self, env):
        # MlpPolicy — самая стабильная политика для простых данных
        self.model = PPO("MlpPolicy", env, verbose=1)

    def train(self, steps=1000):
        print(f"Начинаем обучение агента на {steps} шагах...")
        self.model.learn(total_timesteps=steps)

    def get_action(self, obs):
        action, _ = self.model.predict(obs)
        return action