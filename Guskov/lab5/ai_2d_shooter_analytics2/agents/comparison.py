import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from .epsilon_greedy import EpsilonGreedyAgent
from .random_agent import RandomAgent

class AgentComparator:
    """Сравнение производительности разных агентов"""
    
    def __init__(self, env_wrapper):
        self.env_wrapper = env_wrapper
        self.num_actions = env_wrapper.get_num_actions()
        
        # Создаем агентов для сравнения
        self.agents = {
            'random': RandomAgent(self.num_actions),
            'epsilon_greedy': EpsilonGreedyAgent(self.num_actions, epsilon=0.3),
            'epsilon_greedy_trained': None  # Будет загружен после обучения
        }
    
    def run_comparison(self, episodes=10, steps_per_episode=100):
        """Запуск сравнения агентов"""
        print("📊 Запуск сравнения агентов...")
        
        results = {}
        
        for agent_name, agent in self.agents.items():
            if agent is None:
                continue
                
            print(f"\n🧪 Тестирование агента: {agent_name}")
            
            episode_rewards = []
            episode_steps = []
            
            for episode in range(episodes):
                state = self.env_wrapper.reset()
                total_reward = 0
                
                for step in range(steps_per_episode):
                    action = agent.get_action(state, step)
                    next_state, reward, terminated, _ = self.env_wrapper.step(action)
                    total_reward += reward
                    
                    if isinstance(agent, EpsilonGreedyAgent):
                        agent.update_q_values(state, action, reward, next_state)
                    
                    state = next_state
                    
                    if terminated:
                        break
                
                episode_rewards.append(total_reward)
                episode_steps.append(step + 1)
                
                if episode % 5 == 0:
                    print(f"  Эпизод {episode}: награда={total_reward:.1f}")
            
            results[agent_name] = {
                'rewards': episode_rewards,
                'steps': episode_steps,
                'avg_reward': np.mean(episode_rewards),
                'std_reward': np.std(episode_rewards),
                'avg_steps': np.mean(episode_steps)
            }
        
        return results
    
    def plot_comparison(self, results, save_path="comparison_results.png"):
        """Визуализация сравнения"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Средние награды
        agent_names = list(results.keys())
        avg_rewards = [results[name]['avg_reward'] for name in agent_names]
        std_rewards = [results[name]['std_reward'] for name in agent_names]
        
        bars = axes[0, 0].bar(agent_names, avg_rewards, yerr=std_rewards,
                             capsize=5, color=['skyblue', 'lightgreen', 'salmon'])
        axes[0, 0].set_title('Средние награды агентов')
        axes[0, 0].set_ylabel('Награда')
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # 2. Награды по эпизодам
        for agent_name in agent_names:
            rewards = results[agent_name]['rewards']
            axes[0, 1].plot(range(len(rewards)), rewards, 'o-', 
                           label=agent_name, alpha=0.7)
        axes[0, 1].set_title('Награды по эпизодам')
        axes[0, 1].set_xlabel('Эпизод')
        axes[0, 1].set_ylabel('Награда')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Шаги по эпизодам
        for agent_name in agent_names:
            steps = results[agent_name]['steps']
            axes[1, 0].plot(range(len(steps)), steps, 's-',
                           label=agent_name, alpha=0.7)
        axes[1, 0].set_title('Шаги по эпизодам')
        axes[1, 0].set_xlabel('Эпизод')
        axes[1, 0].set_ylabel('Шаги')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Box plot распределения наград
        reward_data = [results[name]['rewards'] for name in agent_names]
        axes[1, 1].boxplot(reward_data, labels=agent_names)
        axes[1, 1].set_title('Распределение наград')
        axes[1, 1].set_ylabel('Награда')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.suptitle('Сравнение производительности RL-агентов', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Графики сравнения сохранены: {save_path}")
        
        # Текстовый отчет
        report_path = Path(save_path).parent / "comparison_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("📊 ОТЧЕТ СРАВНЕНИЯ АГЕНТОВ\n")
            f.write("=" * 70 + "\n\n")
            
            for agent_name in agent_names:
                stats = results[agent_name]
                f.write(f"{agent_name.upper()}:\n")
                f.write(f"  Средняя награда: {stats['avg_reward']:.2f} ± {stats['std_reward']:.2f}\n")
                f.write(f"  Средние шаги: {stats['avg_steps']:.1f}\n")
                f.write(f"  Лучшая награда: {max(stats['rewards']):.1f}\n")
                f.write(f"  Худшая награда: {min(stats['rewards']):.1f}\n\n")
        
        print(f"📄 Отчет сравнения сохранен: {report_path}")