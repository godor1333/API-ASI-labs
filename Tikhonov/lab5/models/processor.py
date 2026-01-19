from sentence_transformers import SentenceTransformer


class PostProcessor:
    def __init__(self):
        # Модель эмбеддингов из задания
        print("🤖 Загрузка модели MPNet для эмбеддингов...")
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        print("✅ Модель эмбеддингов готова.")

    def get_embedding(self, text):
        """Превращает текст в вектор (список чисел)"""
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def calculate_temperature(self, text):
        """Запасной метод расчета (базовый)"""
        return min(1.0, len(text.split()) / 50)