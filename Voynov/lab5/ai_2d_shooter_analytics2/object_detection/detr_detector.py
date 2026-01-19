# object_detection/detr_detector.py (дополняем существующий)
import torch
from transformers import DetrImageProcessor, DetrForObjectDetection
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

class DETRDetector:
    """Детектор объектов на основе DETR с адаптацией для игр"""
    
    def __init__(self, model_name="facebook/detr-resnet-50", device="cpu"):
        print(f"🔍 Загрузка модели DETR: {model_name}")
        
        try:
            self.device = device
            self.processor = DetrImageProcessor.from_pretrained(model_name)
            self.model = DetrForObjectDetection.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # Специальные классы для игр (адаптируем COCO)
            self.game_classes = {
                0: 'background', 1: 'player', 2: 'enemy', 3: 'bullet', 
                4: 'enemy_bullet', 5: 'obstacle', 6: 'powerup', 7: 'explosion'
            }
            
            print(f"✅ DETR модель загружена на {device}")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки DETR: {e}")
            print("⚠️ Используется простой детектор")
            self.model = None

    def detect(self, frame, threshold=0.5):
        """Детекция объектов на кадре"""
        if self.model is None:
            return []

        try:
            # Преобразуем MinAtar state (10x10x6) в нормальное изображение
            if isinstance(frame, np.ndarray) and len(frame.shape) == 3:
                if frame.shape[2] == 6:  # MinAtar формат
                    # Создаем визуализацию из каналов
                    frame = self._minatar_to_rgb(frame)

            # Увеличиваем разрешение для DETR (минимум 224x224)
            h, w = frame.shape[:2]
            if h < 224 or w < 224:
                scale = max(224 / h, 224 / w)
                new_h, new_w = int(h * scale), int(w * scale)
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
            else:
                new_h, new_w = h, w

            # Конвертируем в PIL
            image = Image.fromarray(frame)

            # Обработка изображения
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)

            # Детекция
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Постобработка результатов
            target_sizes = torch.tensor([image.size[::-1]])
            results = self.processor.post_process_object_detection(
                outputs, target_sizes=target_sizes, threshold=threshold
            )[0]

            # Преобразуем в игровые объекты
            objects = []

            if len(results["scores"]) > 0:
                for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                    # Преобразуем COCO классы в игровые (простая эвристика)
                    game_type = self._coco_to_game_type(label.item(), score.item())

                    # Преобразуем тензоры в float и масштабируем
                    box = box.cpu().numpy()  # Конвертируем в numpy
                    orig_h, orig_w = h, w

                    box_scaled = [
                        float(box[0] * orig_w / new_w),
                        float(box[1] * orig_h / new_h),
                        float(box[2] * orig_w / new_w),
                        float(box[3] * orig_h / new_h)
                    ]
                    box_scaled = [round(i, 2) for i in box_scaled]

                    # Центр объекта
                    center_x = (box_scaled[0] + box_scaled[2]) / 2
                    center_y = (box_scaled[1] + box_scaled[3]) / 2

                    objects.append({
                        'type': game_type,
                        'bbox': box_scaled,
                        'position': (int(center_x), int(center_y)),
                        'confidence': float(score.item()),
                        'label_id': int(label.item())
                    })

            return objects

        except Exception as e:
            print(f"⚠️ Ошибка детекции DETR: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _minatar_to_rgb(self, state):
        """Преобразование MinAtar состояния в RGB изображение"""
        h, w, channels = state.shape
        
        # Создаем цветное изображение
        rgb = np.zeros((h*8, w*8, 3), dtype=np.uint8)  # Увеличиваем масштаб
        
        # Раскрашиваем каналы
        for y in range(h):
            for x in range(w):
                # Канал 0: враги (красные)
                if state[y, x, 0] > 0:
                    rgb[y*8:(y+1)*8, x*8:(x+1)*8] = [255, 0, 0]
                
                # Канал 2: игрок (зеленый)
                elif state[y, x, 2] > 0:
                    rgb[y*8:(y+1)*8, x*8:(x+1)*8] = [0, 255, 0]
                
                # Канал 3: снаряды игрока (желтый)
                elif state[y, x, 3] > 0:
                    rgb[y*8:(y+1)*8, x*8:(x+1)*8] = [255, 255, 0]
                
                # Канал 1: вражеские снаряды (синий)
                elif state[y, x, 1] > 0:
                    rgb[y*8:(y+1)*8, x*8:(x+1)*8] = [0, 0, 255]
                
                # Канал 4: барьеры (серый)
                elif state[y, x, 4] > 0:
                    rgb[y*8:(y+1)*8, x*8:(x+1)*8] = [128, 128, 128]
        
        return rgb

    def _coco_to_game_type(self, coco_label, confidence):
        """Преобразование COCO классов в игровые типы"""
        # Игровые классы COCO для Space Invaders
        player_classes = [1, 2, 3]  # person, bicycle, car
        enemy_classes = [4, 6, 7, 8]  # motorcycle, bus, train, truck
        bullet_classes = [37, 38, 39, 40, 41]  # sports equipment
        obstacle_classes = [62, 63, 64, 65, 67, 70]  # furniture
        powerup_classes = [44, 46, 47, 48, 49, 50, 51]  # food

        if coco_label in player_classes:
            return 'player'
        elif coco_label in enemy_classes:
            return 'enemy'
        elif coco_label in bullet_classes:
            if confidence > 0.6:
                return 'bullet'
            else:
                return 'enemy_bullet'
        elif coco_label in obstacle_classes:
            return 'obstacle'
        elif coco_label in powerup_classes:
            return 'powerup'
        else:
            return 'unknown'

    def visualize_detection(self, frame, detected_objects):
        """Визуализация детекции"""
        # Преобразуем состояние MinAtar в изображение если нужно
        if len(frame.shape) == 3 and frame.shape[2] == 6:
            frame_viz = self._minatar_to_rgb(frame)
        else:
            frame_viz = frame.copy()

        for obj in detected_objects:
            bbox = obj['bbox']
            # Проверяем что координаты не тензоры
            if hasattr(bbox[0], 'item'):  # Если это тензор
                x_min, y_min, x_max, y_max = [coord.item() for coord in bbox]
            else:
                x_min, y_min, x_max, y_max = bbox

            x_min, y_min, x_max, y_max = int(x_min), int(y_min), int(x_max), int(y_max)
            confidence = obj['confidence']
            obj_type = obj['type']

            # Цвета по типам объектов
            colors = {
                'player': (0, 255, 0),  # Зеленый
                'enemy': (0, 0, 255),  # Красный
                'bullet': (255, 255, 0),  # Голубой
                'enemy_bullet': (255, 0, 0),  # Синий
                'powerup': (255, 0, 255),  # Пурпурный
                'obstacle': (128, 128, 128)  # Серый
            }

            color = colors.get(obj_type, (255, 255, 255))

            # Рисуем bounding box
            cv2.rectangle(frame_viz, (x_min, y_min), (x_max, y_max), color, 2)

            # Подпись
            label = f"{obj_type}: {confidence:.2f}"
            cv2.putText(frame_viz, label, (x_min, y_min - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return frame_viz