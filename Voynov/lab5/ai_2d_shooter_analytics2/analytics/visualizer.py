import numpy as np
import cv2
import matplotlib.pyplot as plt
from pathlib import Path

class GameVisualizer:
    """Визуализация игрового процесса"""
    
    def __init__(self):
        print("🎨 Инициализация визуализатора...")
    
    def create_heatmap(self, positions, grid_size=(10, 10), title="Heatmap"):
        """Создание тепловой карты позиций объектов"""
        heatmap = np.zeros(grid_size)
        
        for x, y in positions:
            if 0 <= x < grid_size[1] and 0 <= y < grid_size[0]:
                heatmap[y, x] += 1
        
        # Нормализация
        if heatmap.max() > 0:
            heatmap = heatmap / heatmap.max()
        
        # Визуализация
        plt.figure(figsize=(8, 6))
        plt.imshow(heatmap, cmap='hot', interpolation='nearest')
        plt.colorbar(label='Частота появления')
        plt.title(title)
        plt.xlabel('X координата')
        plt.ylabel('Y координата')
        
        return plt.gcf()
    
    def plot_trajectory(self, positions, title="Траектория агента"):
        """Визуализация траектории движения"""
        if len(positions) < 2:
            return None
        
        x_vals = [p[0] for p in positions]
        y_vals = [p[1] for p in positions]
        
        plt.figure(figsize=(10, 8))
        plt.plot(x_vals, y_vals, 'b-', alpha=0.5, linewidth=1)
        plt.scatter(x_vals, y_vals, c=range(len(positions)), 
                   cmap='viridis', s=20, alpha=0.7)
        
        # Начало и конец
        plt.scatter(x_vals[0], y_vals[0], color='green', s=100, 
                   label='Начало', marker='o')
        plt.scatter(x_vals[-1], y_vals[-1], color='red', s=100, 
                   label='Конец', marker='x')
        
        plt.colorbar(label='Шаг')
        plt.title(title)
        plt.xlabel('X координата')
        plt.ylabel('Y координата')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        return plt.gcf()
    
    def save_visualization(self, fig, filename):
        """Сохранение визуализации"""
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"💾 Визуализация сохранена: {filename}")