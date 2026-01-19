import torch
from transformers import DetrImageProcessor, DetrForObjectDetection
from PIL import Image
import numpy as np


class MazeDetector:
    def __init__(self):
        print("Загрузка модели DETR (facebook/detr-resnet-50)...")
        # Модель из твоего ТЗ
        self.processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
        self.model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

    def analyze_frame(self, frame):
        """
        Принимает скриншот из MiniGrid (numpy array)
        Возвращает список найденных объектов
        """
        image = Image.fromarray(frame)
        inputs = self.processor(images=image, return_tensors="pt")

        with torch.no_grad():
            outputs = self.model(**inputs)

        # Обработка результатов
        target_sizes = torch.tensor([image.size[::-1]])
        results = self.processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.5)[0]

        detections = []
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            box = [round(i, 2) for i in box.tolist()]
            label_name = self.model.config.id2label[label.item()]
            detections.append({
                "label": label_name,
                "confidence": round(score.item(), 3),
                "box": box
            })

        return detections


if __name__ == "__main__":
    detector = MazeDetector()
    print("Детектор успешно инициализирован.")