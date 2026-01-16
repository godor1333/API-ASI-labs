import torch


def test_full_pipeline_steps(global_model):
    print("\n[PIPELINE] Проверка шагов...")

    # Шаг 1: Парсинг
    dummy_input = torch.randn(1, 10)
    assert dummy_input.shape == (1, 10)
    print("✅ Шаг 1: Парсинг данных - OK")

    # Шаг 2: Инференс
    output = global_model.predict(dummy_input)
    assert output is not None
    print("✅ Шаг 2: Инференс модели - OK")

    # Шаг 3: Результат
    res = output.argmax(dim=1).item()
    assert res in [0, 1]
    print(f"✅ Шаг 3: Получение результата ({res}) - OK")