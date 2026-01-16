import gymnasium as gym
import numpy as np
from minigrid.minigrid_env import MiniGridEnv
from minigrid.core.grid import Grid
from minigrid.core.world_object import Wall, Goal, Lava
from minigrid.core.mission import MissionSpace


class CustomMazeEnv(MiniGridEnv):
    def __init__(self, maze_layout, size=13, max_steps=100, render_mode="rgb_array"):
        self.maze_layout = maze_layout
        mission_space = MissionSpace(mission_func=lambda: "find the green goal")

        super().__init__(
            mission_space=mission_space,
            grid_size=size,
            max_steps=max_steps,
            render_mode=render_mode
        )

    def _gen_grid(self, width, height):
        self.grid = Grid(width, height)
        # Внешний контур
        self.grid.wall_rect(0, 0, width, height)

        # 1-Стена, 2-Лава из макета Node.js
        for y in range(self.maze_layout.shape[0]):
            for x in range(self.maze_layout.shape[1]):
                val = self.maze_layout[y, x]
                if val == 1:
                    self.grid.set(x + 1, y + 1, Wall())
                elif val == 2:
                    self.grid.set(x + 1, y + 1, Lava())

        # Финиш
        self.grid.set(width - 2, height - 2, Goal())
        
        # Устанавливаем начальную позицию агента
        # В MiniGrid координаты начинаются с 0, но внешние стены занимают границы
        # Внутренняя область: от (1, 1) до (width-2, height-2)
        # maze_layout[y][x] соответствует grid[x+1][y+1]
        # Ищем первую свободную клетку (где cell is None)
        start_pos = None
        
        # Ищем первую свободную клетку в внутренней области
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                cell = self.grid.get(x, y)
                # Клетка свободна, если она None (пустая) - не стена, не лава, не цель
                if cell is None:
                    start_pos = (x, y)
                    break
            if start_pos is not None:
                break
        
        # Если не нашли свободную клетку, используем (1, 1) по умолчанию
        # MiniGridEnv проверит это при reset() и выдаст ошибку, если клетка занята
        if start_pos is None:
            start_pos = (1, 1)
        
        # Устанавливаем позицию и направление агента
        # MiniGridEnv автоматически разместит агента при вызове reset()
        # и проверит, что start_pos может быть перекрыта (can_overlap())
        self.agent_pos = start_pos
        self.agent_dir = 0

    def step(self, action):
        obs, reward, terminated, truncated, info = super().step(action)
        # Кастомная проверка смерти
        cell = self.grid.get(*self.agent_pos)
        if cell and cell.type == 'lava':
            reward = -1.0
            terminated = True
        return obs, reward, terminated, truncated, info