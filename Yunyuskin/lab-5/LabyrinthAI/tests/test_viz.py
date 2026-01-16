import matplotlib.pyplot as plt
import os


def test_generate_inference_infographic():
    # Имитируем данные уверенности, чтобы график не был пустым
    # Это те объекты, которые ваш агент должен узнавать
    data = {
        'Lava': 0.98,
        'Goal': 0.92,
        'Wall': 0.85,
        'Box': 0.70
    }

    plt.figure(figsize=(10, 6))
    bars = plt.bar(data.keys(), data.values(), color=['#ff4d4d', '#2ecc71', '#3498db', '#95a5a6'])

    plt.title('Inference Confidence per Object (Automated Report)')
    plt.ylabel('Confidence Score (0.0 - 1.0)')
    plt.ylim(0, 1.1)

    # Добавляем подписи процентов над столбиками
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.02, f'{yval * 100}%', ha='center', va='bottom')

    output_path = os.path.join('logs', 'inference_stats.png')

    # Сохранение
    if not os.path.exists('logs'): os.makedirs('logs')
    plt.savefig(output_path)
    plt.close()

    print(f"\n[Успех] Инфографика с данными сохранена в {output_path}")