# Настройка ComfyUI для работы на CPU

## Проблема

ComfyUI по умолчанию пытается использовать CUDA, но у вас установлена CPU-версия PyTorch.

## Решение 1: Запуск ComfyUI на CPU (рекомендуется)

Измените файл `C:\Users\dimon\ComfyUI\comfy\model_management.py`:

Найдите строку (около 188):
```python
def get_torch_device():
    return torch.device(torch.cuda.current_device())
```

Замените на:
```python
def get_torch_device():
    if torch.cuda.is_available():
        return torch.device(torch.cuda.current_device())
    else:
        return torch.device("cpu")
```

Или добавьте в начало файла `main.py` ComfyUI:
```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
```

## Решение 2: Запуск с флагом --cpu

Попробуйте запустить ComfyUI с флагом для CPU:
```bash
python main.py --cpu --port 8188
```

Если такого флага нет, используйте переменную окружения:
```bash
set CUDA_VISIBLE_DEVICES=-1
python main.py --port 8188
```

## Решение 3: Использование проекта без ComfyUI

Проект может работать **без ComfyUI** в stub-режиме:

1. В `config/config.yaml` установлено `method: "stub"` (уже сделано)
2. Проект будет использовать stub-кадры вместо реальной генерации
3. Все остальные функции (оценка, веб-интерфейс) работают полностью

## Проверка

После настройки проверьте:
```bash
python main.py --port 8188
```

Должно запуститься без ошибок CUDA.

## Примечание

- Работа на CPU будет **медленнее**, чем на GPU
- Для генерации видео на CPU может потребоваться много времени
- Для демонстрации пайплайна stub-режим идеален и работает быстро
