import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os


class MazeVisualizer:
    def __init__(self, size):
        self.size = size
        self.heatmap_data = np.zeros((size, size))
        self.failure_points = []  # Координаты, где агент проиграл (лава или тупик)

    def update_route(self, pos):
        """Записывает посещение клетки"""
        x, y = int(pos[0]), int(pos[1])
        if 0 <= x < self.size and 0 <= y < self.size:
            self.heatmap_data[y, x] += 1

    def add_failure(self, pos):
        """Записывает точку 'провала'"""
        self.failure_points.append(pos)

    def save_analytics(self, filename="logs/run_heatmap.png"):
        """Создает и сохраняет тепловую карту"""
        if not os.path.exists('logs'):
            os.makedirs('logs')

        plt.figure(figsize=(10, 8))
        sns.heatmap(self.heatmap_data, annot=True, fmt=".0f", cmap="YlOrRd", cbar=True)

        # Накладываем точки провала (крестики)
        if self.failure_points:
            fx, fy = zip(*self.failure_points)
            plt.scatter(np.array(fx) + 0.5, np.array(fy) + 0.5,
                        marker='x', color='blue', s=100, label='Failure Points')

        plt.title("Тепловая карта маршрута и точки провала")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        plt.savefig(filename)
        plt.close()
        print(f">>> Аналитика сохранена в {filename}")