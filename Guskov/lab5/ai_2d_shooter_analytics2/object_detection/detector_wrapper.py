import time
from utils.model_interface import ModelInterface

class DetectorWrapper(ModelInterface):
    """Обертка для детекторов под generic интерфейс"""
    
    def __init__(self, detector, detector_name):
        super().__init__(f"detector_{detector_name}")
        self.detector = detector
        self.detector_name = detector_name
    
    def predict(self, frame):
        """Детекция объектов"""
        start_time = time.time()
        
        # Вызываем метод детекции
        if hasattr(self.detector, 'detect'):
            objects = self.detector.detect(frame)
        else:
            objects = []
        
        inference_time = time.time() - start_time
        
        self.inference_times.append(inference_time)
        self.total_inferences += 1
        
        # Создаем хэшируемое представление результата
        result_hashable = {
            'count': len(objects),
            'object_types': sorted(list(set([obj.get('type', 'unknown') for obj in objects]))),
            'positions_hash': hash(str([tuple(obj.get('position', (0, 0))) for obj in objects]))
        }
        
        return result_hashable