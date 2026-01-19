# Найди метод _preprocess_state и замени его на:

def _preprocess_state(self, state):
    """Преобразует состояние в тензор для PyTorch"""
    if isinstance(state, np.ndarray):
        # MinAtar имеет shape (10, 10, 6)
        # Преобразуем (H, W, C) → (C, H, W) → (1, C, H, W)
        if len(state.shape) == 3:
            # Транспонируем каналы вперед
            state = np.transpose(state, (2, 0, 1))
        # Добавляем batch dimension
        state = torch.FloatTensor(state).unsqueeze(0)
    return state.to(self.device)

# Также в методе get_inference_info добавь:
def get_inference_info(self, state):
    """Информация об инференсе (для инфографики)"""
    with torch.no_grad():
        state_tensor = self._preprocess_state(state)
        q_values = self.policy_net(state_tensor).cpu().numpy().flatten()
        
        return {
            'q_values': q_values.tolist(),
            'chosen_action': int(np.argmax(q_values)),
            'action_confidences': (np.exp(q_values) / np.sum(np.exp(q_values))).tolist(),
            'epsilon': self.epsilon
        }