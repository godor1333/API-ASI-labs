import numpy as np
import cv2

class SimpleObjectDetector:
    """Простой детектор объектов для MinAtar"""
    
    def __init__(self):
        print("🔍 Инициализация простого детектора объектов...")
        
        # Цвета для разных типов объектов в Space Invaders
        self.object_colors = {
            'player': (0, 255, 255),    # Голубой
            'enemy': (0, 255, 0),       # Зеленый
            'bullet': (255, 255, 255),  # Белый
            'enemy_bullet': (255, 0, 0), # Красный
            'barrier': (128, 128, 128)  # Серый
        }
    
    def detect(self, state):
        """
        Детекция объектов в состоянии MinAtar
        state: numpy array shape (10, 10, 6) для Space Invaders
        """
        objects = []
        
        if len(state.shape) == 3:
            h, w, channels = state.shape
            
            # Для Space Invaders каналы:
            # 0: враги, 1: вражеские снаряды, 2: игрок, 
            # 3: снаряды игрока, 4: барьеры, 5: ??? (пустой)
            
            channel_mapping = {
                0: 'enemy',
                1: 'enemy_bullet',
                2: 'player',
                3: 'bullet',
                4: 'barrier'
            }
            
            for channel in range(channels):
                channel_data = state[:, :, channel]
                
                # Находим ненулевые позиции
                indices = np.where(channel_data > 0)
                
                for y, x in zip(indices[0], indices[1]):
                    obj_type = channel_mapping.get(channel, f'unknown_{channel}')
                    
                    objects.append({
                        'type': obj_type,
                        'position': (x, y),
                        'bbox': (x, y, 1, 1),  # MinAtar объекты - 1 пиксель
                        'confidence': 1.0,
                        'channel': channel
                    })
        
        return objects
    
    def visualize_detection(self, state, detected_objects):
        """
        Визуализация детекции на кадре
        """
        # Преобразуем состояние в изображение
        img = self._state_to_image(state)
        
        # Рисуем bounding boxes
        for obj in detected_objects:
            x, y, w, h = obj['bbox']
            obj_type = obj['type']
            
            # Цвет объекта
            color = self.object_colors.get(obj_type, (255, 255, 255))
            
            # Прямоугольник
            cv2.rectangle(img, (x*4, y*4), ((x+w)*4, (y+h)*4), color, 1)
            
            # Подпись
            cv2.putText(img, obj_type, (x*4, y*4 - 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
            
            # Точка в центре
            center_x, center_y = x*4 + w*2, y*4 + h*2
            cv2.circle(img, (center_x, center_y), 1, color, -1)
        
        # Добавляем информацию
        cv2.putText(img, f"Objects: {len(detected_objects)}", (5, 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return img
    
    def _state_to_image(self, state):
        """Преобразование состояния MinAtar в RGB изображение"""
        if len(state.shape) == 3:
            h, w, channels = state.shape
            img = np.zeros((h*4, w*4, 3), dtype=np.uint8)
            
            # Увеличиваем и раскрашиваем
            for channel in range(min(channels, 3)):
                channel_data = state[:, :, channel]
                for y in range(h):
                    for x in range(w):
                        if channel_data[y, x] > 0:
                            # Увеличиваем в 4 раза и закрашиваем
                            color_val = min(255, channel * 85 + 100)
                            img[y*4:(y+1)*4, x*4:(x+1)*4, channel] = color_val
            
            return img
        return np.zeros((40, 40, 3), dtype=np.uint8)