import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np

class InferenceVisualizer:
    """Визуализация процесса инференса моделей"""
    
    @staticmethod
    def plot_q_values_decision(q_values, chosen_action, title="Q-values Decision"):
        """Визуализация Q-значений при принятии решения"""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # 1. Бар-график Q-значений
        actions = list(range(len(q_values)))
        bars = axes[0].bar(actions, q_values, color='lightblue', edgecolor='black')
        
        # Подсвечиваем выбранное действие
        if 0 <= chosen_action < len(bars):
            bars[chosen_action].set_color('red')
        
        axes[0].set_xlabel('Action')
        axes[0].set_ylabel('Q-value')
        axes[0].set_title('Q-values for each action')
        axes[0].grid(True, alpha=0.3)
        
        # Добавляем значения на столбцы
        for i, (bar, q_val) in enumerate(zip(bars, q_values)):
            axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                        f'{q_val:.2f}', ha='center', va='bottom')
        
        # 2. Softmax вероятности
        if len(q_values) > 0:
            probs = np.exp(q_values) / np.sum(np.exp(q_values))
            bars2 = axes[1].bar(actions, probs, color='lightgreen', edgecolor='black')
            if 0 <= chosen_action < len(bars2):
                bars2[chosen_action].set_color('red')
            
            axes[1].set_xlabel('Action')
            axes[1].set_ylabel('Probability')
            axes[1].set_title('Action probabilities (softmax)')
            axes[1].grid(True, alpha=0.3)
            
            for i, (bar, prob) in enumerate(zip(bars2, probs)):
                axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                            f'{prob:.2%}', ha='center', va='bottom')
        
        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        return fig
    
    @staticmethod
    def plot_inference_timeline(inference_times, title="Inference Timeline"):
        """Таймлайн инференсов"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        timestamps = list(range(len(inference_times)))
        ax.plot(timestamps, inference_times, 'o-', linewidth=2, markersize=4)
        ax.fill_between(timestamps, inference_times, alpha=0.3)
        
        if inference_times:
            avg_time = np.mean(inference_times)
            ax.axhline(y=avg_time, color='r', linestyle='--', label=f'Average: {avg_time*1000:.1f} ms')
        
        ax.set_xlabel('Inference #')
        ax.set_ylabel('Inference Time (s)')
        ax.set_title(title)
        if inference_times:
            ax.legend()
        ax.grid(True, alpha=0.3)
        
        return fig