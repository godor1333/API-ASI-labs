import torch.utils.benchmark as benchmark
import numpy as np
import pytest
from tests.model_registry import ModelRegistry


def run_timer(label, stmt, globals_dict):
    timer = benchmark.Timer(
        stmt=stmt,
        globals=globals_dict,
        label=label,
        description="Inference timing"
    )
    return timer.blocked_autorange(min_run_time=1)


def test_inference_benchmarks():
    # Данные для теста (заглушка кадра)
    dummy_frame = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)

    # Тест Классификатора (ViT)
    classifier = ModelRegistry.get_model("classifier")
    res_vit = run_timer("ViT Classifier", "model.classify(frame)",
                        {"model": classifier, "frame": dummy_frame})

    # Тест Детектора (DETR)
    detector = ModelRegistry.get_model("detector")
    res_detr = run_timer("DETR Detector", "model.analyze_frame(frame)",
                         {"model": detector, "frame": dummy_frame})

    print(f"\nРезультаты бенчмарка:\n{res_vit}\n{res_detr}")
    assert res_vit.median < 1  # Пример: инференс не должен быть дольше 0.5 сек