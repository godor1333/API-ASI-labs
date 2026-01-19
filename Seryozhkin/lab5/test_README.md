# REST API Тесты для brainrot-detector

## Установка зависимостей

Установите тестовые зависимости:

```bash
pip install -r requirements.txt
```

Или установите только тестовые зависимости:

```bash
pip install pytest pytest-asyncio httpx
```

## Запуск тестов

Запустить все тесты:

```bash
pytest
```

Запустить тесты с подробным выводом:

```bash
pytest -v
```

Запустить конкретный тестовый файл:

```bash
pytest test_api.py
```

Запустить конкретный тестовый класс:

```bash
pytest test_api.py::TestAnalyzeEndpoint
```

Запустить конкретный тест:

```bash
pytest test_api.py::TestAnalyzeEndpoint::test_analyze_vk_video_success
```

## Структура тестов

### conftest.py
- Содержит фикстуры для тестирования:
  - `db_session` - тестовая сессия БД (изолированная для каждого теста)
  - `client` - тестовый клиент FastAPI
  - `sample_analysis` - фикстура с примером анализа в БД
  - `setup_mocks` - настройка мок-объектов для parser, tiktok_parser, analyzer

### test_api.py
Содержит REST тесты для всех эндпоинтов:

1. **TestRootEndpoint** - тесты для `GET /`
2. **TestAnalyzeEndpoint** - тесты для `POST /api/analyze`
   - Успешный анализ VK видео
   - Успешный анализ TikTok видео
   - Ошибка при отсутствии URL
   - Ошибка при неподдерживаемом URL
   - Обработка дубликатов
3. **TestParseTrendingEndpoint** - тесты для `POST /api/parse_trending`
4. **TestGetAnalysesEndpoint** - тесты для `GET /api/analyses`
   - Получение пустого списка
   - Получение списка с данными
   - Использование лимита
5. **TestGetAnalysisByIdEndpoint** - тесты для `GET /api/analyses/{analysis_id}`
6. **TestGetStatsEndpoint** - тесты для `GET /api/stats`

## Особенности

- Используется временная тестовая БД (создается для каждого теста)
- Все внешние зависимости (VK parser, TikTok parser, VideoAnalyzer) замокированы
- Тесты изолированы друг от друга
- Не требуется запущенный сервер - используется TestClient из FastAPI

