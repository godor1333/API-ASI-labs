import numpy as np
import random
import pickle
from pathlib import Path

class EpsilonGreedyAgent:
    """Улучшенный ε-greedy агент для Space Invaders"""
    
    def __init__(self, num_actions, epsilon=0.3, alpha=0.2, gamma=0.95):
        self.num_actions = num_actions
        self.epsilon = epsilon  # Начальное значение exploration
        self.alpha = alpha      # Скорость обучения
        self.gamma = gamma      # Коэффициент дисконтирования
        self.q_table = {}       # Таблица Q-значений
        self.state_counts = {}  # Количество посещений состояний
        
        # История для анализа
        self.learning_history = []
        
        print(f"🤖 Агент инициализирован: ε={epsilon}, α={alpha}, γ={gamma}")
    
    def get_action(self, state, step=0):
        """
        Выбор действия по ε-greedy стратегии
        с учетом прогресса обучения
        """
        state_key = self._state_to_key(state)
        
        # Инициализация Q-значений и счетчиков для нового состояния
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.num_actions)
            self.state_counts[state_key] = 0
        
        # Увеличиваем счетчик посещений
        self.state_counts[state_key] = self.state_counts.get(state_key, 0) + 1
        
        # Динамический epsilon (уменьшается с опытом)
        state_visits = self.state_counts[state_key]
        dynamic_epsilon = self.epsilon / (1 + 0.01 * state_visits)
        
        # ε-greedy выбор
        if random.random() < dynamic_epsilon:
            # Случайное исследование
            action = random.randint(0, self.num_actions - 1)
            exploration_type = "random"
        else:
            # Жадная эксплуатация
            q_values = self.q_table[state_key]
            max_q = np.max(q_values)
            
            # Если несколько действий с максимальным Q, выбираем случайное из них
            best_actions = np.where(q_values == max_q)[0]
            action = np.random.choice(best_actions) if len(best_actions) > 0 else random.randint(0, self.num_actions - 1)
            exploration_type = "greedy"
        
        # Запись в историю (только если нужно)
        if step % 10 == 0:  # Сохраняем не каждый шаг
            self.learning_history.append({
                'step': step,
                'state_key': state_key[:20] if len(state_key) > 20 else state_key,
                'action': action,
                'exploration': exploration_type,
                'epsilon_used': dynamic_epsilon,
                'state_visits': state_visits
            })
        
        return action
    
    def update_q_values(self, state, action, reward, next_state):
        """Улучшенное обновление Q-таблицы"""
        state_key = self._state_to_key(state)
        next_state_key = self._state_to_key(next_state)
        
        # Инициализация если нужно
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.num_actions)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.num_actions)
        
        # Текущее Q-значение
        current_q = self.q_table[state_key][action]
        
        # Максимальное Q-значение для следующего состояния
        next_max_q = np.max(self.q_table[next_state_key])
        
        # Формула Q-learning с адаптивным alpha
        visits = self.state_counts.get(state_key, 1)
        adaptive_alpha = self.alpha / (1 + 0.001 * visits)
        
        # Вычисление нового Q-значения
        new_q = current_q + adaptive_alpha * (reward + self.gamma * next_max_q - current_q)
        self.q_table[state_key][action] = new_q
        
        return new_q, adaptive_alpha
    
    def _state_to_key(self, state):
        """Упрощённое преобразование состояния в ключ"""
        # Для быстрой работы используем простой хеш
        try:
            if hasattr(state, 'tobytes'):
                # Преобразуем в bytes и берём хеш
                return str(hash(state.tobytes()))
            
            # Если это numpy array
            if hasattr(state, 'shape'):
                # Более простая версия для MinAtar
                if len(state.shape) == 3:
                    # Бинаризуем и создаём строку
                    binary_state = (state > 0).astype(int)
                    return str(binary_state.tobytes()[:100])  # Берём первые 100 байт
        except:
            pass
        
        # Резервный вариант
        return str(state)
    
    def save_model(self, filepath="models/epsilon_greedy_model.pkl"):
        """Сохранение модели"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            model_data = {
                'q_table': self.q_table,
                'state_counts': self.state_counts,
                'params': {
                    'epsilon': self.epsilon,
                    'alpha': self.alpha,
                    'gamma': self.gamma,
                    'num_actions': self.num_actions
                },
                'learning_history': self.learning_history[-100:]  # Последние 100 записей
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"💾 Модель сохранена: {filepath}")
            print(f"  Размер Q-таблицы: {len(self.q_table)} состояний")
            
        except Exception as e:
            print(f"⚠️ Ошибка сохранения модели: {e}")
    
    def load_model(self, filepath="models/epsilon_greedy_model.pkl"):
        """Загрузка модели"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.q_table = model_data['q_table']
            self.state_counts = model_data.get('state_counts', {})
            
            if 'learning_history' in model_data:
                self.learning_history = model_data['learning_history']
            
            print(f"📂 Модель загружена: {filepath}")
            print(f"  Размер Q-таблицы: {len(self.q_table)} состояний")
            
            return True
        except Exception as e:
            print(f"⚠️ Ошибка загрузки модели: {e}")
            return False
    
    def get_stats(self):
        """Получение статистики агента"""
        total_states = len(self.q_table)
        total_visits = sum(self.state_counts.values()) if self.state_counts else 0
        
        # Анализ exploration/exploitation
        if self.learning_history:
            recent_history = self.learning_history[-50:] if len(self.learning_history) > 50 else self.learning_history
            explorations = [h.get('exploration', 'unknown') for h in recent_history]
            random_actions = sum(1 for e in explorations if e == 'random')
            exploration_rate = random_actions / len(explorations) * 100 if explorations else 0
        else:
            exploration_rate = 0
        
        return {
            'total_states': total_states,
            'total_visits': total_visits,
            'avg_visits_per_state': total_visits / total_states if total_states > 0 else 0,
            'exploration_rate': exploration_rate,
            'current_epsilon': self.epsilon,
            'q_table_size': sum(len(q) for q in self.q_table.values()) if self.q_table else 0
        }