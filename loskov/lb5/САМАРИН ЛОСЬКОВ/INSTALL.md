# Инструкция по установке

## Требования

- Python 3.8+
- CUDA (для GPU ускорения, опционально)
- ComfyUI (для генерации видео через SVD)

## Установка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Установка ComfyUI

ComfyUI должен быть установлен отдельно. Рекомендуется использовать официальный репозиторий:

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

### 3. Установка моделей

#### Stable Video Diffusion

Модели SVD нужно скачать вручную или они будут загружены автоматически при первом использовании:

- `stabilityai/stable-video-diffusion-img2vid-xt`
- `stabilityai/stable-video-diffusion-img2vid-xt-1-1`

#### CLIP

Модель CLIP загрузится автоматически при первом использовании:
- `openai/clip-vit-base-patch32`

#### ImageReward

Для ImageReward может потребоваться дополнительная установка:
```bash
pip install ImageReward
```

### 4. Настройка ComfyUI

**Важно:** Если у вас установлена CPU-версия PyTorch (без CUDA), ComfyUI может не запуститься. 

#### Решение для CPU:

1. **Вариант 1:** Добавьте в начало `ComfyUI/main.py`:
```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
```

2. **Вариант 2:** Измените `ComfyUI/comfy/model_management.py`:
Найдите функцию `get_torch_device()` и замените на:
```python
def get_torch_device():
    if torch.cuda.is_available():
        return torch.device(torch.cuda.current_device())
    else:
        return torch.device("cpu")
```

3. Запустите ComfyUI:
```bash
cd ComfyUI
python main.py --port 8188
```

4. Убедитесь, что ComfyUI доступен на `http://localhost:8188`

**Примечание:** Проект может работать **без ComfyUI** в stub-режиме (см. NO_MODELS_README.md)

### 5. Настройка конфигурации

Отредактируйте `config/config.yaml` при необходимости:

- Измените `comfyui.host` и `comfyui.port` если ComfyUI запущен на другом адресе
- Настройте параметры генерации (fps, длительность клипов и т.д.)
- Настройте параметры оценки (частота кадров для анализа и т.д.)

## Проверка установки

Запустите тестовую генерацию:

```bash
python main.py full "кот-программист бежит по коду"
```

Или используйте примеры:

```bash
python example_usage.py
```

## Запуск веб-интерфейса

```bash
cd frontend
python app.py
```

Интерфейс будет доступен на `http://localhost:5000`

## Структура директорий

После первого запуска будут созданы следующие директории:

- `outputs/keyframes/` - ключевые кадры
- `outputs/videos/` - сгенерированные видео
- `results/` - результаты оценки
- `results/benchmark/` - результаты бенчмарков
- `results/comparisons/` - результаты сравнений моделей
