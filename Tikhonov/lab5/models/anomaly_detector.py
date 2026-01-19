from transformers import pipeline

class AnomalyDetector:
    def __init__(self):
        print("🔥 Загрузка модели DistilBert для анализа температуры...")
        # Используем модель из задания для анализа интенсивности
        self.temp_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased"
        )
        print("✅ Модель температуры готова.")

    def analyze_temperature(self, text):
        """Вычисляет коэффициент активности (score) через DistilBert"""
        try:
            # Ограничиваем длину текста для модели (512 токенов)
            result = self.temp_analyzer(text[:512])[0]
            return result['score']
        except Exception as e:
            print(f"⚠️ Ошибка при анализе температуры: {e}")
            return 0.0

    def check_anomaly(self, recent_count):
        """Выявляет аномалию на основе частоты упоминаний в районе"""
        return 1 if recent_count > 5 else 0