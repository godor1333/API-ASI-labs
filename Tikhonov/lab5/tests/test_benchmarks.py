import torch
import torch.utils.benchmark as benchmark


def test_native_benchmark(global_model):
    print("\n[BENCHMARK] Запуск нативного замера скорости...")
    data = torch.randn(1, 10)

    t = benchmark.Timer(
        stmt='model.predict(data)',
        globals={'model': global_model, 'data': data}
    )
    m = t.timeit(50)
    print(f"\nРезультат:\n{m}")
    assert m.mean < 1.0  # Время должно быть меньше секунды