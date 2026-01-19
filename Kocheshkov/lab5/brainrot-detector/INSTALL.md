# Инструкция по установке для Python 3.13

Если возникают проблемы с установкой зависимостей на Python 3.13, выполните установку по шагам:

## Способ 1: Использование скрипта установки

```bash
install.bat
```

## Способ 2: Ручная установка

### 1. Сначала установите numpy (только бинарные пакеты):

```bash
pip install --only-binary :all: numpy>=2.0.0
```

Если это не работает, попробуйте:

```bash
pip install numpy
```

### 2. Затем установите остальные зависимости:

```bash
pip install -r requirements.txt
```

## Способ 3: Установка критичных пакетов по отдельности

Если проблемы продолжаются, установите пакеты группами:

```bash
# Основные веб-фреймворки
pip install fastapi uvicorn[standard] python-multipart

# База данных
pip install sqlalchemy

# ML библиотеки (могут занять время)
pip install torch torchvision transformers

# Обработка медиа
pip install opencv-python-headless librosa pillow

# Остальные
pip install pydantic aiohttp beautifulsoup4 yt-dlp plotly pandas jinja2 python-dotenv ffmpeg-python scikit-learn sentencepiece
```

## Альтернатива: Использование Python 3.11 или 3.12

Если проблемы с Python 3.13 продолжаются, рекомендуется использовать Python 3.11 или 3.12, которые имеют лучшую поддержку всех пакетов:

1. Установите Python 3.11 или 3.12 с python.org
2. Создайте виртуальное окружение:
   ```bash
   python3.11 -m venv venv
   venv\Scripts\activate
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```



