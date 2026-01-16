import torch
import torch.nn as nn
import os

# 1. Определяем архитектуру
class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(10, 2)
    def forward(self, x):
        return self.fc(x)

# 2. Создаем модель и сохраняем ТОЛЬКО ВЕСА (state_dict)
model = SimpleModel()
os.makedirs("models", exist_ok=True)
torch.save(model.state_dict(), "models/prod_model.pt")
print("✅ Файл весов (state_dict) успешно создан.")