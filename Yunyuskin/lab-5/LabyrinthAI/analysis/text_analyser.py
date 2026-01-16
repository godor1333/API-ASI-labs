from sentence_transformers import SentenceTransformer, util


class LoopDetector:
    def __init__(self):
        # Модель из ТЗ: multi-qa-mpnet-base-dot-v1
        self.model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')
        self.history = []

    def check_loop(self, action_text):
        self.history.append(action_text)
        if len(self.history) < 4: return False

        # Сравниваем текущее действие с тем, что было 2 шага назад
        embeddings = self.model.encode([self.history[-1], self.history[-3]])
        score = util.cos_sim(embeddings[0], embeddings[1])
        return score > 0.85  # Если похожи - значит ходит кругами