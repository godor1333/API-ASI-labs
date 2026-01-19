import json
import numpy as np

def generate_maze():
    """Генерирует простой лабиринт в формате JSON"""
    width = 11
    height = 11
    
    # Создаем базовую карту (0 = проход, 1 = стена, 2 = лава)
    # Начинаем с заполнения стенами
    maze_data = np.ones((height, width), dtype=int)
    
    # Создаем простой проход от (1,1) до (9,9)
    # Горизонтальные проходы
    for y in [1, 3, 5, 7, 9]:
        for x in range(1, width-1):
            maze_data[y, x] = 0
    
    # Вертикальные проходы
    for x in [1, 3, 5, 7, 9]:
        for y in range(1, height-1):
            maze_data[y, x] = 0
    
    # Добавляем лаву в некоторых тупиках
    lava_positions = [(2, 2), (4, 4), (6, 6), (8, 8)]
    for y, x in lava_positions:
        if 0 < y < height-1 and 0 < x < width-1:
            maze_data[y, x] = 2
    
    # Сохраняем в JSON (формат ожидаемый main.py)
    result = {
        "width": width,
        "height": height,
        "map": maze_data.tolist()  # 2D массив для main.py
    }
    
    with open("maze.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"Лабиринт {width}x{height} создан и сохранен в maze.json")
    return result

if __name__ == "__main__":
    generate_maze()
