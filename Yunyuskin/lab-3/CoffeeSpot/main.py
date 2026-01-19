import gymnasium as gym
import pygame
import numpy as np
import os
from stable_baselines3 import PPO
from env.custom_env import CustomMazeEnv  # Исправлено: CustomMazeEnv вместо CustomLabyrinthEnv
from analysis.visualizer import MazeVisualizer  # Исправлено: MazeVisualizer вместо Visualizer
import json


def load_maze_config(path="maze.json"):
    # Получаем абсолютный путь к файлу относительно директории скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, path)
    
    # Проверяем существование файла
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Файл {full_path} не найден! Убедитесь, что файл maze.json существует в директории {script_dir}")
    
    try:
        # Используем utf-8-sig для автоматического удаления BOM, если он есть
        with open(full_path, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            # Проверяем структуру данных
            if 'map' not in data:
                raise ValueError("В файле maze.json отсутствует ключ 'map'")
            return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка при чтении JSON файла {full_path}: {e}")


if __name__ == "__main__":
    # 1. Загружаем конфигурацию, созданную генератором
    maze_config = load_maze_config()

    # 2. Инициализируем среду (custom_env.py)
    # Преобразуем список в numpy array
    maze_layout = np.array(maze_config['map'])
    base_env = CustomMazeEnv(maze_layout=maze_layout, size=13, max_steps=200, render_mode="human")
    
    # Важно: инициализируем среду перед созданием модели
    print("Инициализация среды...")
    obs, _ = base_env.reset()
    print(f"Observation space: {base_env.observation_space}")
    print(f"Action space: {base_env.action_space}")

    print("Загрузка агента и запуск теста...")

    # 3. Создаем обертку для stable-baselines3
    # MiniGrid использует Dict observation space, нужно преобразовать в вектор
    from stable_baselines3.common.vec_env import DummyVecEnv
    from gymnasium.wrappers import FlattenObservation
    from gymnasium import spaces
    import numpy as np
    
    # Wrapper для преобразования Dict observation в плоский вектор
    class DictFlattenWrapper(gym.Wrapper):
        def __init__(self, env):
            super().__init__(env)
            # Преобразуем Dict observation space в Box
            if isinstance(env.observation_space, spaces.Dict):
                # Извлекаем размеры из всех компонентов Dict
                # Пропускаем MissionSpace (строки)
                flat_dim = 0
                for key, space in env.observation_space.spaces.items():
                    if key == 'mission':
                        continue  # Пропускаем mission (строка)
                    if isinstance(space, spaces.Box):
                        flat_dim += np.prod(space.shape)
                    elif isinstance(space, spaces.Discrete):
                        flat_dim += 1  # Одно значение для дискретного пространства
                
                self.observation_space = spaces.Box(
                    low=-np.inf, high=np.inf, shape=(flat_dim,), dtype=np.float32
                )
            else:
                self.observation_space = env.observation_space
        
        def _flatten_obs(self, obs):
            """Преобразует Dict observation в плоский вектор"""
            if isinstance(obs, dict):
                flat_obs = []
                for key in sorted(obs.keys()):  # Сортируем для консистентности
                    val = obs[key]
                    if isinstance(val, np.ndarray):
                        # Массивы (например, изображение)
                        flat_obs.append(val.flatten())
                    elif isinstance(val, (int, np.integer)):
                        # Дискретные значения (например, direction)
                        flat_obs.append(np.array([float(val)]))
                    elif isinstance(val, str):
                        # Строки (например, mission) - пропускаем или кодируем
                        # Для простоты пропускаем mission, так как это текстовое описание
                        continue
                    else:
                        # Другие типы - пытаемся преобразовать в число
                        try:
                            flat_obs.append(np.array([float(val)]))
                        except (ValueError, TypeError):
                            # Если не получается, пропускаем
                            continue
                
                if len(flat_obs) == 0:
                    # Если ничего не осталось, возвращаем нулевой вектор
                    return np.array([0.0], dtype=np.float32)
                
                return np.concatenate(flat_obs).astype(np.float32)
            return obs.astype(np.float32) if isinstance(obs, np.ndarray) else np.array([obs], dtype=np.float32)
        
        def step(self, action):
            obs, reward, terminated, truncated, info = self.env.step(action)
            return self._flatten_obs(obs), reward, terminated, truncated, info
        
        def reset(self, **kwargs):
            obs, info = self.env.reset(**kwargs)
            return self._flatten_obs(obs), info
    
    # Создаем функцию-фабрику для среды
    def make_env():
        env = CustomMazeEnv(maze_layout=maze_layout, size=13, max_steps=200, render_mode="rgb_array")
        env = DictFlattenWrapper(env)
        return env
    
    # Оборачиваем среду для векторизации
    env = DummyVecEnv([make_env])
    
    # Используем MlpPolicy для векторизованных наблюдений
    model = PPO("MlpPolicy", env, verbose=1, device="cpu")
    model.learn(total_timesteps=10000)

    # 4. Основной цикл визуализации (используем оригинальную среду для рендеринга)
    obs, _ = base_env.reset()
    running = True

    # Инициализируем визуализатор для сбора данных
    maze_size = maze_config.get('width', 11)
    visualizer = MazeVisualizer(size=maze_size)

    while running:
        # Получаем действие от модели
        # Преобразуем наблюдение в формат, который ожидает модель
        # Модель обучена на плоских векторах (DictFlattenWrapper)
        obs_for_model = None
        if isinstance(obs, dict):
            # Преобразуем Dict в плоский вектор (как в DictFlattenWrapper)
            flat_obs = []
            for key in sorted(obs.keys()):
                if key == 'mission':
                    continue  # Пропускаем mission (строка)
                val = obs[key]
                if isinstance(val, np.ndarray):
                    flat_obs.append(val.flatten())
                elif isinstance(val, (int, np.integer)):
                    flat_obs.append(np.array([float(val)]))
                else:
                    try:
                        flat_obs.append(np.array([float(val)]))
                    except (ValueError, TypeError):
                        continue
            if len(flat_obs) > 0:
                obs_for_model = np.concatenate(flat_obs).astype(np.float32)
            else:
                obs_for_model = np.array([0.0], dtype=np.float32)
        else:
            obs_for_model = obs.astype(np.float32) if isinstance(obs, np.ndarray) else np.array([obs], dtype=np.float32)
        
        # Предсказываем действие (нужно добавить batch dimension для vec_env)
        if len(obs_for_model.shape) == 1:  # (n,)
            obs_for_model = obs_for_model[np.newaxis, ...]  # (1, n)
        
        action, _ = model.predict(obs_for_model, deterministic=True)
        # Если action - массив, берем первый элемент
        if isinstance(action, np.ndarray):
            if action.size > 1:
                action = int(action.item() if action.size == 1 else action[0].item())
            else:
                action = int(action.item())
        elif not isinstance(action, (int, np.integer)):
            action = int(action)
        
        obs, reward, terminated, truncated, info = base_env.step(action)

        # Отрисовка через env
        base_env.render()

        # Собираем координаты для тепловой карты (используем agent_pos из env)
        if hasattr(base_env, 'agent_pos'):
            visualizer.update_route(base_env.agent_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if terminated or truncated:
            print("Тест завершен!")
            break

    pygame.quit()

    # 5. СОХРАНЕНИЕ ТЕПЛОВОЙ КАРТЫ
    # Используем метод из анализатора
    visualizer.save_analytics("logs/run_heatmap.png")
    print("Файл тепловой карты сохранен в logs/run_heatmap.png")