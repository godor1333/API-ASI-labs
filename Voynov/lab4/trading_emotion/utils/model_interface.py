import time
from abc import ABC, abstractmethod
import numpy as np

class ModelInterface(ABC):
    """Generic интерфейс для всех моделей (детекторы, агенты)"""
    
    def __init__(self, model_name):
        self.model_name = model_name
        self.inference_times = []
        self.total_inferences = 0
    
    @abstractmethod
    def predict(self, input_data):
        """Основной метод предсказания"""
        pass
    
    def benchmark_inference(self, test_input, n_iterations=100):
        """Бенчмарк скорости инференса"""
        print(f"  ⏱️  Бенчмарк {self.model_name} ({n_iterations} итераций)...")
        
        times = []
        for i in range(n_iterations):
            start_time = time.time()
            _ = self.predict(test_input)
            times.append(time.time() - start_time)
        
        avg_time = np.mean(times)
        fps = 1 / avg_time if avg_time > 0 else 0
        
        return {
            'model_name': self.model_name,
            'avg_inference_time_ms': avg_time * 1000,
            'fps': fps,
            'std_time_ms': np.std(times) * 1000,
            'min_time_ms': np.min(times) * 1000,
            'max_time_ms': np.max(times) * 1000,
            'n_iterations': n_iterations
        }
    
    def test_consistency(self, test_input, n_runs=10):
        """Тест консистентности (одинаковые результаты)"""
        print(f"  🧪 Тест консистентности {self.model_name} ({n_runs} прогонов)...")
        
        results = []
        for i in range(n_runs):
            result = self.predict(test_input)
            results.append(result)
        
        # Простая проверка: считаем хэши результатов
        result_hashes = [hash(str(result)) for result in results]
        is_consistent = len(set(result_hashes)) == 1
        
        return {
            'model_name': self.model_name,
            'is_consistent': is_consistent,
            'n_runs': n_runs,
            'all_results_match': is_consistent,
            'unique_results': len(set(result_hashes))
        }