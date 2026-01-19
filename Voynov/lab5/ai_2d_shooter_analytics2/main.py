import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from env_wrapper.minatar_wrapper import MinAtarWrapper
from agents.epsilon_greedy import EpsilonGreedyAgent
from agents.random_agent import RandomAgent
from object_detection.simple_detector import SimpleObjectDetector
from analytics.metrics import GameMetrics
from analytics.visualizer import GameVisualizer
from utils.logger import GameLogger
import numpy as np
import cv2
from pathlib import Path
import time


def main():
    """Основной запуск проекта"""
    print("=" * 70)
    print("🚀 Проект: Анализ поведения AI-ботов в 2D-шутере")
    print("=" * 70)

    # 1. Инициализация логгера
    logger = GameLogger()
    logger.log_training_start({"game": "space_invaders", "agent": "epsilon_greedy"})

    try:
        # 2. Инициализация среды
        print("\n🎮 Инициализация игры...")
        env_wrapper = MinAtarWrapper("space_invaders")
        logger.logger.info(f"Среда создана: {env_wrapper.game_name}")

        # 3. Инициализация агента
        print("🤖 Создание ε-greedy агента...")
        agent = EpsilonGreedyAgent(
            num_actions=env_wrapper.get_num_actions(),
            epsilon=0.2
        )
        logger.logger.info(f"Агент создан: ε={agent.epsilon}")

        # 4. Инициализация детектора объектов
        print("🔍 Инициализация детектора объектов...")
        detector = SimpleObjectDetector()

        # 5. Инициализация аналитики
        print("📊 Инициализация системы аналитики...")
        metrics = GameMetrics()
        visualizer = GameVisualizer()

        # 6. Обучение агента
        print("\n🎯 Начало обучения...")
        num_episodes = 5  # Начнем с 5 эпизодов
        steps_per_episode = 100

        # Для тепловой карты
        all_positions = []

        for episode in range(num_episodes):
            logger.log_episode_start(episode, agent.epsilon)
            print(f"\n📈 Эпизод {episode + 1}/{num_episodes}")

            state = env_wrapper.reset()
            total_reward = 0
            episode_positions = []

            for step in range(steps_per_episode):
                # Детекция объектов
                detected_objects = detector.detect(state)

                # Выбор действия агентом
                action = agent.get_action(state, step)

                # Шаг в среде
                next_state, reward, terminated, _ = env_wrapper.step(action)
                total_reward += reward

                # Обновление агента
                agent.update_q_values(state, action, reward, next_state)

                # Запись метрик
                metrics.record_step(
                    episode=episode,
                    step=step,
                    action=action,
                    reward=reward,
                    objects_detected=len(detected_objects),
                    state=state
                )

                # Логирование
                logger.log_step(episode, step, action, reward, total_reward, len(detected_objects))

                # Сохранение позиции игрока для тепловой карты
                for obj in detected_objects:
                    if obj['type'] == 'player':
                        episode_positions.append(obj['position'])
                        all_positions.append(obj['position'])

                state = next_state

                # Сохранение кадра каждый 20-й шаг в первом эпизоде
                if episode == 0 and step % 20 == 0:
                    img = detector.visualize_detection(state, detected_objects)
                    cv2.imwrite(f"training_frame_ep{episode}_step{step}.png", img)

                if terminated:
                    logger.logger.info(f"Игра завершена на шаге {step}")
                    break

            logger.log_episode_end(episode, total_reward, min(step, steps_per_episode), agent.epsilon)
            print(f"  🏆 Награда эпизода: {total_reward:.1f}")
            print(f"  📊 Обнаружено объектов: {metrics.get_avg_objects(episode):.1f}/шаг")

            # Постепенное уменьшение epsilon
            agent.epsilon = max(0.05, agent.epsilon * 0.95)

        # 7. Сохранение результатов
        print("\n💾 Сохранение результатов...")
        results_dir = Path("training_results")
        results_dir.mkdir(exist_ok=True)

        # Сохранение отчетов
        metrics.save_report(results_dir / "training_report.txt")
        metrics.plot_training_progress(results_dir / "training_plots.png")

        # Создание тепловых карт
        if all_positions:
            heatmap = visualizer.create_heatmap(
                all_positions,
                grid_size=(10, 10),
                title="Тепловая карта позиций игрока"
            )
            visualizer.save_visualization(
                heatmap,
                results_dir / "player_heatmap.png"
            )

        logger.log_training_end({
            "episodes": num_episodes,
            "final_epsilon": agent.epsilon,
            "total_positions": len(all_positions)
        })

        print(f"\n✅ Обучение завершено!")
        print(f"📁 Результаты в папке: {results_dir}/")

        # 8. Тестирование обученного агента
        print("\n🎮 Тестирование обученного агента...")
        test_agent_performance(env_wrapper, agent, detector, logger)

        # 9. Сравнение со случайным агентом
        print("\n📊 Сравнение с случайным агентом...")
        compare_with_random(env_wrapper, detector, metrics)

    except Exception as e:
        logger.logger.error(f"Ошибка в основном потоке: {e}")
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


def test_agent_performance(env, agent, detector, logger):
    """Тестирование производительности агента"""
    print("🧪 Запуск тестового прогона...")

    state = env.reset()
    total_reward = 0
    test_positions = []

    # Отключаем exploration для теста
    original_epsilon = agent.epsilon
    agent.epsilon = 0.0

    for step in range(50):
        # Детекция объектов
        objects = detector.detect(state)

        # Действие агента
        action = agent.get_action(state, step)

        # Шаг
        next_state, reward, terminated, _ = env.step(action)
        total_reward += reward

        # Сохранение позиции
        for obj in objects:
            if obj['type'] == 'player':
                test_positions.append(obj['position'])

        # Визуализация
        if step % 10 == 0:
            frame = detector.visualize_detection(state, objects)
            cv2.imwrite(f"test_frame_{step:03d}.png", frame)
            print(f"  Шаг {step}: Действие={action}, Награда={reward:.1f}")

        state = next_state

        if terminated:
            print(f"  🎮 Игра завершена на шаге {step}")
            break

    # Восстанавливаем epsilon
    agent.epsilon = original_epsilon

    print(f"🏁 Тест завершен! Итоговая награда: {total_reward:.1f}")
    logger.logger.info(f"Тестирование агента: награда={total_reward:.1f}, шагов={step}")

    # Сохранение тепловой карты теста
    if test_positions:
        visualizer = GameVisualizer()
        heatmap = visualizer.create_heatmap(
            test_positions,
            grid_size=(10, 10),
            title="Тепловая карта тестового прогона"
        )
        visualizer.save_visualization(
            heatmap,
            "test_heatmap.png"
        )


def compare_with_random(env, detector, metrics):
    """Сравнение с случайным агентом"""
    print("🎲 Тестирование случайного агента...")

    random_agent = RandomAgent(env.get_num_actions())
    state = env.reset()
    total_reward = 0

    for step in range(50):
        # Действие случайного агента
        action = random_agent.get_action()

        # Шаг
        next_state, reward, terminated, _ = env.step(action)
        total_reward += reward

        state = next_state

        if terminated:
            break

    print(f"🎲 Случайный агент: награда = {total_reward:.1f}")

    # Сравнение с обученным агентом
    trained_stats = metrics.get_training_summary()
    if trained_stats and trained_stats['episodes']:
        last_episode_reward = trained_stats['episodes'][-1]['total_reward']
        improvement = ((total_reward - last_episode_reward) / abs(last_episode_reward) * 100
                       if last_episode_reward != 0 else 0)

        print(f"\n📊 СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ:")
        print(f"  🎯 Обученный агент (последний эпизод): {last_episode_reward:.1f}")
        print(f"  🎲 Случайный агент: {total_reward:.1f}")
        print(f"  📈 Разница: {total_reward - last_episode_reward:+.1f}")
        print(f"  📊 Изменение: {improvement:+.1f}%")


if __name__ == "__main__":
    main()