import torch
from transformers import ViTImageProcessor, ViTForImageClassification
from PIL import Image


class SituationClassifier:
    def __init__(self):
        # Модель из ТЗ: nateraw/vit-base-beans
        self.processor = ViTImageProcessor.from_pretrained("nateraw/vit-base-beans")
        self.model = ViTForImageClassification.from_pretrained("nateraw/vit-base-beans")

    def classify(self, frame):
        image = Image.fromarray(frame)
        inputs = self.processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Если индекс предсказания высокий - помечаем как Опасно
        label = outputs.logits.argmax(-1).item()
        return "ОПАСНО" if label == 1 else "БЕЗОПАСНО"