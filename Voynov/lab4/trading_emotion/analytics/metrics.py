import numpy as np
import json
from pathlib import Path
from datetime import datetime

class GameMetrics:
    """Сбор и анализ метрик игры"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Сброс метрик"""
        self.episodes_data = []
        self.current_episode = {
            'steps': [],
            'total_reward': 0,
            'objects_detected': [],
            'actions_taken': {}
        }
    
    def record_step(self, episode, step, action, reward, objects_detected, state=None):
        """Запись данных шага"""
        # Инициализация эпизода если нужно
        while len(self.episodes_data) <= episode:
            self.episodes_data.append({
                'steps': [],
                'total_reward': 0,
                'objects_detected': [],
                'actions_taken': {},
                'start_time': datetime.now()
            })
        
        # Запись данных шага
        step_data = {
            'step': step,
            'action': int(action),
            'reward': float(reward),
            'objects_detected': int(objects_detected),
            'timestamp': datetime.now().isoformat()
        }
        
        self.episodes_data[episode]['steps'].append(step_data)
        self.episodes_data[episode]['total_reward'] += reward
        
        # Статистика действий
        action_key = str(action)
        if action_key not in self.episodes_data[episode]['actions_taken']:
            self.episodes_data[episode]['actions_taken'][action_key] = 0
        self.episodes_data[episode]['actions_taken'][action_key] += 1
        
        # Статистика объектов
        self.episodes_data[episode]['objects_detected'].append(objects_detected)
    
    def get_episode_stats(self, episode):
        """Получить статистику эпизода"""
        if episode >= len(self.episodes_data):
            return None
        
        ep_data = self.episodes_data[episode]
        steps = len(ep_data['steps'])
        
        if steps == 0:
            return None
        
        # Собираем статистику
        rewards = [s['reward'] for s in ep_data['steps']]
        objects = ep_data['objects_detected']
        
        stats = {
            'episode': episode,
            'total_steps': steps,
            'total_reward': ep_data['total_reward'],
            'avg_reward': np.mean(rewards) if rewards else 0,
            'max_reward': max(rewards) if rewards else 0,
            'min_reward': min(rewards) if rewards else 0,
            'avg_objects': np.mean(objects) if objects else 0,
            'total_actions': sum(ep_data['actions_taken'].values()),
            'action_distribution': ep_data['actions_taken']
        }
        
        return stats
    
    def get_avg_objects(self, episode):
        """Среднее количество объектов в эпизоде"""
        stats = self.get_episode_stats(episode)
        return stats['avg_objects'] if stats else 0
    
    def get_training_summary(self):
        """Сводка по всем эпизодам"""
        if not self.episodes_data:
            return None
        
        all_rewards = [ep['total_reward'] for ep in self.episodes_data]
        all_steps = [len(ep['steps']) for ep in self.episodes_data]
        
        summary = {
            'total_episodes': len(self.episodes_data),
            'total_steps': sum(all_steps),
            'avg_reward_per_episode': np.mean(all_rewards) if all_rewards else 0,
            'max_reward': max(all_rewards) if all_rewards else 0,
            'min_reward': min(all_rewards) if all_rewards else 0,
            'avg_steps_per_episode': np.mean(all_steps) if all_steps else 0,
            'episodes': []
        }
        
        # Добавляем статистику по каждому эпизоду
        for i in range(len(self.episodes_data)):
            ep_stats = self.get_episode_stats(i)
            if ep_stats:
                summary['episodes'].append(ep_stats)
        
        return summary
    
    def save_report(self, filepath):
        """Сохранение отчета в файл"""
        summary = self.get_training_summary()
        
        if not summary:
            print("⚠️ Нет данных для отчета")
            return
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("📊 ОТЧЕТ ПО ОБУЧЕНИЮ RL-АГЕНТА\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("📈 СВОДНАЯ СТАТИСТИКА:\n")
            f.write(f"  Всего эпизодов: {summary['total_episodes']}\n")
            f.write(f"  Всего шагов: {summary['total_steps']}\n")
            f.write(f"  Средняя награда за эпизод: {summary['avg_reward_per_episode']:.2f}\n")
            f.write(f"  Максимальная награда: {summary['max_reward']:.2f}\n")
            f.write(f"  Минимальная награда: {summary['min_reward']:.2f}\n")
            f.write(f"  Среднее шагов за эпизод: {summary['avg_steps_per_episode']:.1f}\n\n")
            
            f.write("📋 ДЕТАЛЬНАЯ СТАТИСТИКА ПО ЭПИЗОДАМ:\n")
            for ep in summary['episodes']:
                f.write(f"\n  Эпизод {ep['episode']+1}:\n")
                f.write(f"    Шагов: {ep['total_steps']}\n")
                f.write(f"    Общая награда: {ep['total_reward']:.2f}\n")
                f.write(f"    Средняя награда: {ep['avg_reward']:.2f}\n")
                f.write(f"    Среднее объектов: {ep['avg_objects']:.1f}\n")
                
                # Распределение действий
                if ep['action_distribution']:
                    f.write(f"    Распределение действий:\n")
                    for action, count in sorted(ep['action_distribution'].items()):
                        percentage = count / ep['total_steps'] * 100
                        f.write(f"      Действие {action}: {count} ({percentage:.1f}%)\n")
        
        print(f"💾 Отчет сохранен: {filepath}")
    
    def plot_training_progress(self, filepath):
        """Создание графиков прогресса обучения"""
        try:
            import matplotlib.pyplot as plt
            
            if not self.episodes_data:
                print("⚠️ Нет данных для графиков")
                return
            
            # Данные для графиков
            episodes = list(range(len(self.episodes_data)))
            rewards = [ep['total_reward'] for ep in self.episodes_data]
            steps = [len(ep['steps']) for ep in self.episodes_data]
            
            # Создаем график
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            
            # 1. Награды по эпизодам
            axes[0, 0].plot(episodes, rewards, 'b-o', linewidth=2, markersize=4)
            axes[0, 0].set_title('Награды по эпизодам')
            axes[0, 0].set_xlabel('Эпизод')
            axes[0, 0].set_ylabel('Награда')
            axes[0, 0].grid(True, alpha=0.3)
            
            # 2. Скользящее среднее наград
            if len(rewards) > 1:
                window = min(5, len(rewards) // 2)
                moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')
                axes[0, 1].plot(episodes[window-1:], moving_avg, 'r-', linewidth=2)
                axes[0, 1].set_title(f'Скользящее среднее наград (окно={window})')
                axes[0, 1].set_xlabel('Эпизод')
                axes[0, 1].set_ylabel('Награда')
                axes[0, 1].grid(True, alpha=0.3)
            
            # 3. Шаги по эпизодам
            axes[1, 0].plot(episodes, steps, 'g-o', linewidth=2, markersize=4)
            axes[1, 0].set_title('Шаги по эпизодам')
            axes[1, 0].set_xlabel('Эпизод')
            axes[1, 0].set_ylabel('Шаги')
            axes[1, 0].grid(True, alpha=0.3)
            
            # 4. Гистограмма действий (последний эпизод)
            if self.episodes_data:
                last_ep = self.episodes_data[-1]
                if last_ep['actions_taken']:
                    actions = list(last_ep['actions_taken'].keys())
                    counts = list(last_ep['actions_taken'].values())
                    
                    bars = axes[1, 1].bar(actions, counts, color='skyblue', edgecolor='black')
                    axes[1, 1].set_title('Распределение действий (последний эпизод)')
                    axes[1, 1].set_xlabel('Действие')
                    axes[1, 1].set_ylabel('Количество')
                    
                    # Добавляем значения на столбцы
                    for bar, count in zip(bars, counts):
                        height = bar.get_height()
                        axes[1, 1].text(bar.get_x() + bar.get_width()/2., height,
                                       f'{count}', ha='center', va='bottom')
            
            plt.suptitle('Прогресс обучения RL-агента', fontsize=14, fontweight='bold')
            plt.tight_layout()
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"📈 Графики сохранены: {filepath}")
            
        except Exception as e:
            print(f"⚠️ Ошибка при создании графиков: {e}")