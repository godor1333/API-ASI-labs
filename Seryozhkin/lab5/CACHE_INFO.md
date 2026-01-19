# Настройка кэша Hugging Face на диск H

## Автоматическая настройка

Кэш моделей Hugging Face теперь автоматически сохраняется на диск H: в папке `H:\brainrot-detector\models_cache\`

## Что было сделано:

1. **Обновлен `config.py`** - автоматически устанавливает переменные окружения для кэша на диск H
2. **Обновлен `video_analyzer.py`** - использует кэш на диске H при загрузке моделей
3. **Обновлены скрипты запуска** - устанавливают переменные окружения перед запуском

## Структура кэша:

```
H:\brainrot-detector\models_cache\
├── hub\              # Основной кэш моделей (CLIP, ViT, Whisper)
├── transformers\     # Кэш transformers библиотеки
└── datasets\        # Кэш датасетов
```

## Переменные окружения:

- `HF_HOME` = `H:\brainrot-detector\models_cache` (основная директория кэша)
- `HF_HUB_CACHE` = `H:\brainrot-detector\models_cache\hub`
- `HF_DATASETS_CACHE` = `H:\brainrot-detector\models_cache\datasets`

**Примечание:** `TRANSFORMERS_CACHE` устарела и больше не используется. Используйте `HF_HOME` вместо неё.

## Примечание:

Если модели уже были скачаны на диск C: (`C:\Users\asd\.cache\huggingface\`), они будут использоваться оттуда. 
Для полного переноса на диск H можно:
1. Скопировать файлы из `C:\Users\asd\.cache\huggingface\hub\` в `H:\brainrot-detector\models_cache\hub\`
2. Или просто удалить старый кэш - модели скачаются заново на диск H

## Размер моделей:

- CLIP: ~700 МБ
- ViT: ~300 МБ  
- Whisper Large v3: ~3 ГБ

**Итого: ~4 ГБ** - все будет на диске H:



