# Установка Custom Nodes для ComfyUI

## Проблема

Ошибка: `Cannot execute because node StableVideoDiffusionLoader does not exist`

Это означает, что в ComfyUI не установлены custom nodes для Stable Video Diffusion.

## Решение

### Вариант 1: Использовать stub-режим (рекомендуется для демо)

Проект автоматически переключится на stub-режим, если ноды не найдены. Это нормально для демонстрации пайплайна.

### Вариант 2: Установить custom nodes для SVD

Если нужна реальная генерация через ComfyUI:

1. **Установите ComfyUI-Manager** (менеджер custom nodes):
```bash
cd ComfyUI
git clone https://github.com/ltdrdata/ComfyUI-Manager.git custom_nodes/ComfyUI-Manager
```

2. **Установите ноды для Stable Video Diffusion:**
   - Через ComfyUI-Manager в веб-интерфейсе
   - Или вручную найдите и установите ноды для SVD

3. **Альтернатива:** Используйте встроенные ноды ComfyUI для работы с видео

### Вариант 3: Использовать другой workflow

Можно изменить `generate_svd_workflow()` в `backend/comfyui_client.py` для использования стандартных нод ComfyUI вместо SVD.

## Текущее поведение

Проект автоматически:
- ✅ Обнаруживает отсутствие нод
- ✅ Переключается на stub-режим
- ✅ Продолжает работу без ошибок
- ✅ Генерирует видео из stub-кадров
- ✅ Выполняет оценку через Webench2

**Для демонстрации пайплайна это идеально!**
