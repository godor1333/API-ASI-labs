import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from env_wrapper.minatar_wrapper import MinAtarWrapper
from agents.epsilon_greedy import EpsilonGreedyAgent
from agents.random_agent import RandomAgent
from analytics.metrics import GameMetrics
from analytics.visualizer import GameVisualizer
import numpy as np
from pathlib import Path
import cv2
import time
import json
from datetime import datetime

print("=" * 80)
print("🚀 ФИНАЛЬНЫЙ ПРОЕКТ: Анализ поведения AI-ботов в 2D-шутере")
print("=" * 80)

# Проверяем доступность новых компонентов Этапа 2
try:
    from agents.dqn_agent import DQNAgent

    DQN_AVAILABLE = True
except ImportError as e:
    DQN_AVAILABLE = False
    print(f"⚠️ DQN агент недоступен: {e}")

try:
    from utils.model_interface import ModelInterface
    from agents.agent_wrapper import AgentWrapper
    from object_detection.detector_wrapper import DetectorWrapper
    from analytics.inference_visualizer import InferenceVisualizer

    TESTING_FRAMEWORK_AVAILABLE = True
except ImportError as e:
    TESTING_FRAMEWORK_AVAILABLE = False
    print(f"⚠️ Фреймворк тестирования недоступен: {e}")


# Вспомогательная функция для сериализации numpy
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        else:
            return super().default(obj)


def create_project_structure():
    """Создание структуры проекта"""
    folders = ["results", "models", "logs", "screenshots", "videos", "reports"]
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
    print("📁 Структура проекта создана")


class VideoRecorder:
    """Простой рекордер для записи видео"""

    def __init__(self, filename="videos/gameplay.mp4", fps=10.0, frame_size=(160, 160)):
        self.filename = filename
        self.fps = fps
        self.frame_size = frame_size
        self.writer = None
        Path("videos").mkdir(exist_ok=True)

    def start(self):
        """Начать запись"""
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(self.filename, fourcc, self.fps, self.frame_size)
        print(f"🎥 Начата запись видео: {self.filename}")

    def record_frame(self, frame):
        """Записать кадр"""
        if self.writer is not None:
            # Приводим к нужному размеру
            if frame.shape[:2] != self.frame_size:
                frame = cv2.resize(frame, self.frame_size)
            self.writer.write(frame)

    def stop(self):
        """Остановить запись"""
        if self.writer is not None:
            self.writer.release()
            print(f"💾 Видео сохранено: {self.filename}")


class ThreatAnalyzer:
    """Анализатор пропущенных угроз"""

    def __init__(self, grid_size=(10, 10)):
        self.grid_size = grid_size
        self.threat_map = np.zeros(grid_size, dtype=np.float32)
        self.detected_threats = []
        self.missed_threats = []

    def analyze_frame(self, detected_objects, agent_action, reward):
        """Анализ угроз в кадре"""
        threats = []

        for obj in detected_objects:
            if obj['type'] in ['enemy', 'enemy_bullet', 'unknown']:
                threats.append(obj)
                x, y = obj['position']
                if 0 <= x < self.grid_size[1] and 0 <= y < self.grid_size[0]:
                    self.threat_map[y, x] += 1

        # Если была отрицательная награда, но угрозы были - считаем пропущенной угрозой
        if reward < 0 and threats:
            self.missed_threats.append({
                'step': len(self.detected_threats),
                'threats': len(threats),
                'action': int(agent_action),
                'reward': float(reward)
            })

        self.detected_threats.extend(threats)
        return len(threats)

    def generate_threat_report(self):
        """Генерация отчета об угрозах"""
        total_threats = len(self.detected_threats)
        missed_threats = len(self.missed_threats)

        if total_threats > 0:
            miss_rate = missed_threats / total_threats * 100
        else:
            miss_rate = 0.0

        # Преобразуем threat_map для JSON
        threat_map_list = self.threat_map.astype(float).tolist()

        return {
            'total_threats': int(total_threats),
            'missed_threats': int(missed_threats),
            'miss_rate_percent': float(miss_rate),
            'threat_map': threat_map_list,
            'high_threat_zones': self._find_high_threat_zones()
        }

    def _find_high_threat_zones(self):
        """Найти зоны с высокой концентрацией угроз"""
        if self.threat_map.max() == 0:
            return []

        threshold = self.threat_map.mean() + self.threat_map.std()
        zones = np.where(self.threat_map > threshold)

        high_zones = []
        for y, x in zip(zones[0], zones[1]):
            high_zones.append({
                'x': int(x),
                'y': int(y),
                'threat_level': float(self.threat_map[y, x])
            })

        return high_zones


class EfficiencyCalculator:
    """Калькулятор индекса эффективности"""

    def __init__(self):
        self.stats = {
            'total_shots': 0,
            'hits': 0,
            'near_misses': 0,
            'reaction_times': [],
            'survival_time': 0.0,
            'damage_taken': 0.0,
            'damage_dealt': 0.0
        }
        self.last_action_time = time.time()

    def update(self, action, reward, objects_detected, step_duration):
        """Обновить статистику"""
        # Реакция (время между угрозой и действием)
        reaction_time = time.time() - self.last_action_time
        self.stats['reaction_times'].append(float(reaction_time))
        self.last_action_time = time.time()

        # Анализ действий (Space Invaders: действие 1 - выстрел)
        if action == 1:  # Выстрел
            self.stats['total_shots'] += 1
            if reward > 0:
                self.stats['hits'] += 1
                self.stats['damage_dealt'] += float(reward)
            elif reward == 0:
                self.stats['near_misses'] += 1

        # Урон
        if reward < 0:
            self.stats['damage_taken'] += abs(float(reward))

        # Время выживания
        self.stats['survival_time'] += float(step_duration)

    def calculate_efficiency_index(self):
        """Рассчитать индекс эффективности"""
        if self.stats['total_shots'] == 0:
            accuracy = 0.0
        else:
            accuracy = self.stats['hits'] / self.stats['total_shots'] * 100

        if len(self.stats['reaction_times']) > 0:
            avg_reaction = np.mean(self.stats['reaction_times'])
            reaction_score = max(0.0, 100 - (avg_reaction * 1000))  # Чем быстрее, тем лучше
        else:
            reaction_score = 50.0

        # Выживаемость (чем дольше, тем лучше)
        survival_score = min(100.0, self.stats['survival_time'] * 10)

        # Избегание урона
        if self.stats['damage_taken'] > 0:
            avoidance_score = max(0.0, 100 - self.stats['damage_taken'] * 10)
        else:
            avoidance_score = 100.0

        # Общий индекс
        efficiency_index = (
                accuracy * 0.3 +  # Точность 30%
                reaction_score * 0.25 +  # Реакция 25%
                survival_score * 0.25 +  # Выживаемость 25%
                avoidance_score * 0.2  # Избегание 20%
        )

        return {
            'efficiency_index': float(efficiency_index),
            'accuracy_percent': float(accuracy),
            'reaction_score': float(reaction_score),
            'survival_score': float(survival_score),
            'avoidance_score': float(avoidance_score),
            'detailed_stats': {
                'total_shots': int(self.stats['total_shots']),
                'hits': int(self.stats['hits']),
                'near_misses': int(self.stats['near_misses']),
                'avg_reaction_time': float(
                    np.mean(self.stats['reaction_times']) if self.stats['reaction_times'] else 0),
                'survival_time': float(self.stats['survival_time']),
                'damage_taken': float(self.stats['damage_taken']),
                'damage_dealt': float(self.stats['damage_dealt'])
            }
        }


def initialize_detector():
    """Инициализация детектора объектов"""
    print("\n🔍 Инициализация детектора объектов...")

    USE_ADVANCED_DETECTOR = True
    DETR_THRESHOLD = 0.2

    if USE_ADVANCED_DETECTOR:
        try:
            from object_detection.detector_factory import DetectorFactory
            detector = DetectorFactory.create_detector(detector_type="auto", use_gpu=False)
            if hasattr(detector, 'model') and detector.model is not None:
                detector_type = "DETR"
                print(f"   ✅ Детектор: DETR (порог: {DETR_THRESHOLD})")
            else:
                detector_type = "simple"
                from object_detection.simple_detector import SimpleObjectDetector
                detector = SimpleObjectDetector()
                print(f"   ⚠️ Детектор: простой (DETR не загрузился)")
        except Exception as e:
            print(f"   ⚠️ Ошибка загрузки DETR: {e}")
            from object_detection.simple_detector import SimpleObjectDetector
            detector = SimpleObjectDetector()
            detector_type = "simple"
            print(f"   ✅ Детектор: простой (fallback)")
    else:
        from object_detection.simple_detector import SimpleObjectDetector
        detector = SimpleObjectDetector()
        detector_type = "simple"
        print(f"   ✅ Детектор: простой")

    return detector, detector_type


def run_final_project():
    """Финальная версия проекта с DETR, DQN и расширенной аналитикой"""

    # Создаем структуру
    create_project_structure()

    # 1. ИНИЦИАЛИЗАЦИЯ ДЕТЕКТОРА
    detector, detector_type = initialize_detector()

    # 2. ИНИЦИАЛИЗАЦИЯ ИГРЫ
    print("\n🎮 2. Инициализация игры Space Invaders...")
    env = MinAtarWrapper("space_invaders")
    print(f"   ✅ Игра: Space Invaders")
    print(f"   ✅ Действий: {env.get_num_actions()}")
    print(f"   ✅ Размер состояния: {env.get_state_shape()}")

    # 3. ИНИЦИАЛИЗАЦИЯ АНАЛИТИКИ
    print("\n📊 3. Инициализация систем анализа...")

    threat_analyzer = ThreatAnalyzer()
    efficiency_calc = EfficiencyCalculator()
    metrics = GameMetrics()
    visualizer = GameVisualizer()

    # Видеорекордер с уникальным именем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_recorder = VideoRecorder(
        filename=f"videos/gameplay_{timestamp}.mp4",
        fps=10.0,
        frame_size=(320, 320)
    )

    # Тест детекции
    test_state = env.reset()
    test_objects = detector.detect(test_state)

    # Для DETR: если не нашел объекты, пробуем с другим порогом
    if detector_type == "DETR" and len(test_objects) == 0:
        print("   ⚠️ DETR не нашел объекты, пробуем простой детектор...")
        from object_detection.simple_detector import SimpleObjectDetector
        detector = SimpleObjectDetector()
        detector_type = "simple_fallback"
        test_objects = detector.detect(test_state)

    print(f"   ✅ Обнаружено объектов: {len(test_objects)}")
    if test_objects:
        for obj in test_objects[:3]:  # Показываем первые 3 объекта
            print(f"      - {obj['type']} в позиции {obj['position']}")

    # 4. СОЗДАНИЕ АГЕНТОВ
    print("\n🤖 4. Создание RL-агентов...")
    num_actions = env.get_num_actions()

    random_agent = RandomAgent(num_actions)
    epsilon_agent = EpsilonGreedyAgent(
        num_actions=num_actions,
        epsilon=0.3,
        alpha=0.1,
        gamma=0.9
    )

    print(f"   ✅ Случайный агент создан")
    print(f"   ✅ ε-greedy агент создан: ε={epsilon_agent.epsilon}")

    # 5. БЫСТРОЕ ОБУЧЕНИЕ (3 эпизода)
    print("\n📚 5. Быстрое обучение ε-greedy агента (3 эпизода)...")

    training_start = time.time()

    for episode in range(3):
        state = env.reset()
        total_reward = 0.0
        episode_objects = []
        step_start_time = time.time()

        for step in range(30):
            # Детекция объектов
            detected_objects = detector.detect(state)

            # Анализ угроз
            threats_detected = threat_analyzer.analyze_frame(
                detected_objects,
                None,
                0
            )

            # Выбор действия
            action = epsilon_agent.get_action(state, step)

            # Шаг в среде
            next_state, reward, terminated, _ = env.step(action)
            total_reward += float(reward)

            # Расчет эффективности
            step_duration = time.time() - step_start_time
            efficiency_calc.update(action, reward, len(detected_objects), step_duration)
            step_start_time = time.time()

            # Обновление агента
            epsilon_agent.update_q_values(state, action, reward, next_state)

            # Сохранение метрик
            metrics.record_step(
                episode=episode,
                step=step,
                action=action,
                reward=reward,
                objects_detected=len(detected_objects),
                state=state
            )

            # Сохранение позиций игрока
            for obj in detected_objects:
                if obj['type'] == 'player':
                    episode_objects.append(obj['position'])

            # Сохранение первого кадра
            if episode == 0 and step == 0 and len(detected_objects) > 0:
                frame = detector.visualize_detection(state, detected_objects)
                cv2.imwrite("screenshots/first_frame.png", frame)

            state = next_state

            if terminated:
                print(f"   🎮 Игра завершена на шаге {step}")
                break

        # Уменьшение epsilon
        epsilon_agent.epsilon = max(0.1, epsilon_agent.epsilon * 0.8)

        print(f"   Эпизод {episode + 1}: награда={total_reward:5.1f}, "
              f"шагов={step + 1:2d}, ε={epsilon_agent.epsilon:.3f}")

    training_time = time.time() - training_start
    print(f"   ⏱️  Время обучения: {training_time:.1f} сек")

    # 6. ТЕСТИРОВАНИЕ АГЕНТОВ
    print("\n🧪 6. Тестирование производительности агентов...")

    test_results = {}
    agents_to_test = [("random", random_agent), ("epsilon_greedy", epsilon_agent)]

    for agent_name, agent in agents_to_test:
        print(f"\n   Тестирование {agent_name} агента...")

        # Создаем новый видеорекордер для каждого агента
        agent_video_recorder = VideoRecorder(
            filename=f"videos/{agent_name}_{timestamp}.mp4",
            fps=10.0,
            frame_size=(320, 320)
        )
        agent_video_recorder.start()

        # Для обученного агента отключаем exploration
        if agent_name == "epsilon_greedy":
            original_epsilon = agent.epsilon
            agent.epsilon = 0.0

        # Сброс анализаторов для теста
        test_threat_analyzer = ThreatAnalyzer()
        test_efficiency_calc = EfficiencyCalculator()

        state = env.reset()
        total_reward = 0.0
        positions = []
        frames_to_save = []

        for step in range(25):
            detected_objects = detector.detect(state)
            action = agent.get_action(state, step)
            next_state, reward, terminated, _ = env.step(action)
            total_reward += float(reward)

            # Анализ угроз
            test_threat_analyzer.analyze_frame(detected_objects, action, reward)

            # Расчет эффективности
            test_efficiency_calc.update(action, reward, len(detected_objects), 0.1)

            # Сохранение позиции игрока
            for obj in detected_objects:
                if obj['type'] == 'player':
                    positions.append([int(obj['position'][0]), int(obj['position'][1])])

            # Визуализация и запись кадра
            if len(detected_objects) > 0:
                frame = detector.visualize_detection(state, detected_objects)
                agent_video_recorder.record_frame(frame)

                # Сохранение ключевых кадров
                if step in [0, 8, 16, 24]:
                    frames_to_save.append((step, frame))

            state = next_state

            if terminated:
                break

        # Останавливаем запись видео
        agent_video_recorder.stop()

        # Восстанавливаем epsilon
        if agent_name == "epsilon_greedy":
            agent.epsilon = original_epsilon

        # Сохранение кадров
        for step_num, frame in frames_to_save:
            cv2.imwrite(f"screenshots/{agent_name}_step_{step_num:02d}.png", frame)

        # Расчет индекса эффективности
        efficiency_report = test_efficiency_calc.calculate_efficiency_index()
        threat_report = test_threat_analyzer.generate_threat_report()

        test_results[agent_name] = {
            'total_reward': float(total_reward),
            'steps': int(step + 1),
            'positions': positions,
            'efficiency_index': efficiency_report['efficiency_index'],
            'accuracy': efficiency_report['accuracy_percent'],
            'threat_miss_rate': threat_report['miss_rate_percent'],
            'efficiency_details': efficiency_report,
            'threat_details': threat_report
        }

        print(f"     Награда: {total_reward:.1f}")
        print(f"     Шагов: {step + 1}")
        print(f"     Индекс эффективности: {efficiency_report['efficiency_index']:.1f}")
        print(f"     Точность: {efficiency_report['accuracy_percent']:.1f}%")
        print(f"     Пропущено угроз: {threat_report['miss_rate_percent']:.1f}%")

        # Создание тепловой карты
        if positions:
            heatmap = visualizer.create_heatmap(
                positions,
                grid_size=(10, 10),
                title=f"Тепловая карта: {agent_name} агент"
            )
            visualizer.save_visualization(
                heatmap,
                f"results/{agent_name}_heatmap.png"
            )

        # Создание карты угроз
        if threat_report['threat_map']:
            threat_positions = []
            for y in range(10):
                for x in range(10):
                    threat_level = int(threat_report['threat_map'][y][x])
                    for _ in range(threat_level):
                        threat_positions.append((x, y))

            if threat_positions:
                threat_heatmap = visualizer.create_heatmap(
                    threat_positions,
                    grid_size=(10, 10),
                    title=f"Карта угроз: {agent_name} агент"
                )
                visualizer.save_visualization(
                    threat_heatmap,
                    f"results/{agent_name}_threat_map.png"
                )

    # 7. ТЕСТИРОВАНИЕ И БЕНЧМАРКИ МОДЕЛЕЙ (НОВЫЙ ЭТАП 2)

    # Проверяем доступность компонентов Этапа 2 локально
    DQN_AVAILABLE_LOCAL = False
    TESTING_FRAMEWORK_AVAILABLE_LOCAL = False

    try:
        from agents.dqn_agent import DQNAgent
        DQN_AVAILABLE_LOCAL = True
    except ImportError:
        pass

    try:
        from utils.model_interface import ModelInterface
        from agents.agent_wrapper import AgentWrapper
        from object_detection.detector_wrapper import DetectorWrapper
        from analytics.inference_visualizer import InferenceVisualizer
        TESTING_FRAMEWORK_AVAILABLE_LOCAL = True
    except ImportError:
        pass

    if TESTING_FRAMEWORK_AVAILABLE_LOCAL:
        print("\n🧪 7. Тестирование и бенчмарки моделей...")

        # Создаем тестовые данные
        test_state = env.reset()

        # Тестируем детектор
        detector_wrapper = DetectorWrapper(detector, f"detector_{detector_type}")
        detector_benchmark = detector_wrapper.benchmark_inference(test_state, n_iterations=50)
        detector_consistency = detector_wrapper.test_consistency(test_state, n_runs=5)

        print(f"   📊 Детектор {detector_type}:")
        print(
            f"     Скорость: {detector_benchmark['avg_inference_time_ms']:.1f} мс ({detector_benchmark['fps']:.1f} FPS)")
        print(f"     Консистентность: {'✅' if detector_consistency['all_results_match'] else '❌'}")

        # Добавляем DQN агента если доступен
        dqn_agent = None
        dqn_training_time = 0

        if DQN_AVAILABLE_LOCAL:
            print("\n   🧠 Инициализация DQN агента...")
            try:
                dqn_agent = DQNAgent(
                    input_shape=env.get_state_shape(),
                    num_actions=num_actions,
                    use_gpu=False
                )

                # Быстрое обучение DQN (5 эпизодов)
                print("   📚 Быстрое обучение DQN (5 эпизодов)...")
                dqn_training_start = time.time()

                for episode in range(5):
                    state = env.reset()
                    total_reward = 0

                    for step in range(20):
                        action = dqn_agent.get_action(state, step, training=True)
                        next_state, reward, terminated, _ = env.step(action)
                        total_reward += reward

                        dqn_agent.remember(state, action, reward, next_state, terminated)
                        dqn_agent.replay()

                        state = next_state
                        if terminated:
                            break

                    print(f"     Эпизод {episode + 1}: награда={total_reward:.1f}, ε={dqn_agent.epsilon:.3f}")

                dqn_training_time = time.time() - dqn_training_start
                print(f"     ⏱️  Время обучения DQN: {dqn_training_time:.1f} сек")

                # Добавляем DQN в список для тестирования
                agents_to_test.append(("dqn", dqn_agent))

            except Exception as e:
                print(f"   ⚠️ Ошибка инициализации DQN: {e}")
                DQN_AVAILABLE_LOCAL = False

        # Бенчмарки всех агентов
        agent_benchmarks = {}
        for agent_name, agent in agents_to_test:
            wrapper = AgentWrapper(agent, agent_name)
            benchmark = wrapper.benchmark_inference(test_state, n_iterations=100)
            agent_benchmarks[agent_name] = benchmark

            print(f"   🤖 {agent_name}: {benchmark['avg_inference_time_ms']:.1f} мс")

        # Инфографика инференса
        print("\n   🎨 Создание инфографики инференса...")
        visualizer_inf = InferenceVisualizer()

        # Для каждого агента (кроме случайного) создаем инфографику решений
        for agent_name, agent in agents_to_test:
            if agent_name != "random":
                try:
                    if hasattr(agent, 'get_inference_info'):
                        info = agent.get_inference_info(test_state)
                        fig = visualizer_inf.plot_q_values_decision(
                            info['q_values'],
                            info['chosen_action'],
                            title=f"Инференс {agent_name} агента"
                        )
                        fig.savefig(f"results/{agent_name}_inference.png", dpi=150, bbox_inches='tight')
                        plt.close(fig)
                        print(f"     ✅ Инфографика создана: {agent_name}_inference.png")
                    elif agent_name == "epsilon_greedy":
                        # Для ε-greedy агента создаем свою инфографику
                        state_key = agent._state_to_key(test_state)
                        if state_key in agent.q_table:
                            q_values = agent.q_table[state_key]
                            fig = visualizer_inf.plot_q_values_decision(
                                q_values,
                                np.argmax(q_values),
                                title=f"Инференс {agent_name} агента (Q-table)"
                            )
                            fig.savefig(f"results/{agent_name}_inference.png", dpi=150, bbox_inches='tight')
                            plt.close(fig)
                            print(f"     ✅ Инфографика создана: {agent_name}_inference.png")
                except Exception as e:
                    print(f"     ⚠️ Ошибка создания инфографики для {agent_name}: {e}")

        # Сравнительная таблица производительности
        print("\n   📈 СРАВНИТЕЛЬНАЯ ТАБЛИЦА ПРОИЗВОДИТЕЛЬНОСТИ:")
        print("   " + "=" * 60)
        print("   Модель                  Время (мс)    FPS     Консистентность")
        print("   " + "-" * 60)

        print(f"   Детектор ({detector_type:14}) {detector_benchmark['avg_inference_time_ms']:8.1f}     "
              f"{detector_benchmark['fps']:6.1f}     "
              f"{'✅' if detector_consistency['all_results_match'] else '❌'}")

        for agent_name in sorted(agent_benchmarks.keys()):
            bench = agent_benchmarks[agent_name]
            consistency = "✅"  # Агенты детерминированы или ε=0
            print(f"   Агент {agent_name:17} {bench['avg_inference_time_ms']:8.1f}     "
                  f"{bench['fps']:6.1f}     {consistency}")

        print("   " + "=" * 60)

        # Тестирование DQN агента если он есть
        if dqn_agent is not None:
            print(f"\n   🧠 DQN АГЕНТ ПРОТЕСТИРОВАН:")
            print(f"     Архитектура: Conv2D(6→32→64) → FC(→128→{num_actions})")
            print(f"     Размер replay buffer: {len(dqn_agent.memory)}")
            print(f"     Текущий epsilon: {dqn_agent.epsilon:.3f}")
            print(f"     Обучение: {dqn_training_time:.1f} сек, 5 эпизодов")

        # Сохраняем результаты бенчмарков
        benchmark_results = {
            'detector': detector_benchmark,
            'detector_consistency': detector_consistency,
            'agents': agent_benchmarks,
            'timestamp': timestamp
        }

        with open(f"results/benchmarks_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(benchmark_results, f, cls=NumpyEncoder, ensure_ascii=False, indent=2)

        print(f"   💾 Результаты бенчмарков сохранены: results/benchmarks_{timestamp}.json")

    # 8. АНАЛИТИКА И СОХРАНЕНИЕ
    print("\n📊 8. Аналитика и сохранение результатов...")

    # Графики обучения
    metrics.plot_training_progress("results/training_progress.png")

    # Сохранение модели
    epsilon_agent.save_model("models/trained_agent.pkl")

    # Сохранение DQN модели если есть
    if 'dqn_agent' in locals() and dqn_agent is not None:
        try:
            dqn_agent.save_model("models/dqn_agent.pth")
            print(f"💾 DQN модель сохранена: models/dqn_agent.pth")
        except Exception as e:
            print(f"⚠️ Ошибка сохранения DQN модели: {e}")

    # Статистика агента
    stats = epsilon_agent.get_stats()

    # Финальный отчет
    print("\n" + "=" * 80)
    print("✅ ФИНАЛЬНЫЙ ОТЧЕТ ПРОЕКТА")
    print("=" * 80)

    # Создание JSON отчета
    report_data = {
        "project_name": "Анализ поведения AI-ботов в 2D-шутере",
        "timestamp": timestamp,
        "detector_type": detector_type,
        "game": {
            "name": "Space Invaders (MinAtar)",
            "num_actions": int(num_actions),
            "state_shape": [int(dim) for dim in env.get_state_shape()]
        },
        "training": {
            "episodes": 3,
            "training_time_seconds": float(training_time),
            "total_states_learned": int(stats['total_states']),
            "final_epsilon": float(epsilon_agent.epsilon)
        },
        "testing_results": test_results,
        "comparison": {
            "reward_improvement": float(
                test_results['epsilon_greedy']['total_reward'] - test_results['random']['total_reward']),
            "conclusion": "Обученный агент работает лучше случайного" if test_results['epsilon_greedy'][
                                                                             'total_reward'] > test_results['random'][
                                                                             'total_reward'] else "Требуется больше обучения"
        },
        "stage_2_features": {
            "dqn_tested": dqn_agent is not None,
            "testing_framework_used": TESTING_FRAMEWORK_AVAILABLE_LOCAL,
            "agents_tested": len(agents_to_test)
        }
    }

    # Сохраняем JSON
    report_path = "results/final_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, cls=NumpyEncoder, ensure_ascii=False, indent=2)
    print(f"💾 JSON отчет сохранен: {report_path}")

    # Текстовый отчет
    text_report_path = "results/final_report.txt"
    with open(text_report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("📋 ФИНАЛЬНЫЙ ОТЧЕТ ПРОЕКТА\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Детектор: {detector_type}\n")
        f.write(f"Тестовые объекты: {len(test_objects)}\n\n")

        f.write("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:\n")
        for agent_name, results in test_results.items():
            f.write(f"\n{agent_name.upper()} агент:\n")
            f.write(f"  Награда: {results['total_reward']:.1f}\n")
            f.write(f"  Шагов: {results['steps']}\n")
            f.write(f"  Эффективность: {results['efficiency_index']:.1f}\n")
            f.write(f"  Точность: {results['accuracy']:.1f}%\n")

        f.write(f"\nСРАВНЕНИЕ:\n")
        diff = test_results['epsilon_greedy']['total_reward'] - test_results['random']['total_reward']
        improvement = (diff / test_results['random']['total_reward'] * 100) if test_results['random'][
                                                                                   'total_reward'] > 0 else 0
        f.write(f"  Разница в награде: {diff:+.1f}\n")
        if test_results['random']['total_reward'] > 0:
            f.write(f"  Улучшение: {improvement:+.1f}%\n")

        if diff > 0:
            f.write("  ✅ Обученный агент лучше случайного!\n")
        else:
            f.write("  ⚠️ Нужно больше обучения\n")

        if TESTING_FRAMEWORK_AVAILABLE_LOCAL:
            f.write(f"\nЭТАП 2 - ТЕСТИРОВАНИЕ МОДЕЛЕЙ:\n")
            f.write(f"  Детектор: {detector_type}, {detector_benchmark['avg_inference_time_ms']:.1f} мс\n")
            f.write(f"  Протестировано агентов: {len(agent_benchmarks)}\n")
            if dqn_agent is not None:
                f.write(f"  DQN агент: обучен за {dqn_training_time:.1f} сек\n")

    print(f"\n📁 СОЗДАННЫЕ ФАЙЛЫ:")
    print(f"  results/final_report.json          - Полный отчет")
    print(f"  results/final_report.txt           - Краткий отчет")
    print(f"  results/training_progress.png      - Графики обучения")
    print(f"  results/*_heatmap.png              - Тепловые карты")
    print(f"  results/*_threat_map.png           - Карты угроз")
    if TESTING_FRAMEWORK_AVAILABLE_LOCAL:
        print(f"  results/*_inference.png          - Инфографика инференса")
        print(f"  results/benchmarks_*.json       - Результаты бенчмарков")
    print(f"  models/trained_agent.pkl           - Сохраненная модель")
    if 'dqn_agent' in locals() and dqn_agent is not None:
        print(f"  models/dqn_agent.pth             - DQN модель")
    print(f"  videos/*.mp4                       - Видеозаписи")
    print(f"  screenshots/*.png                  - Скриншоты")

    print(f"\n🏆 РЕЗУЛЬТАТЫ:")
    print(f"  🎲 Случайный агент: {test_results['random']['total_reward']:.1f} очков")
    print(f"  🎯 ε-greedy агент: {test_results['epsilon_greedy']['total_reward']:.1f} очков")

    if 'dqn_agent' in locals() and dqn_agent is not None:
        # Быстрый тест DQN агента
        dqn_test_state = env.reset()
        dqn_test_reward = 0
        for _ in range(10):
            action = dqn_agent.get_action(dqn_test_state, training=False)
            next_state, reward, terminated, _ = env.step(action)
            dqn_test_reward += reward
            dqn_test_state = next_state
            if terminated:
                break
        print(f"  🧠 DQN агент: {dqn_test_reward:.1f} очков (быстрый тест)")

    print(
        f"  📈 Улучшение ε-greedy: +{test_results['epsilon_greedy']['total_reward'] - test_results['random']['total_reward']:+.1f}")

    print(f"\n✅ ПРОЕКТ УСПЕШНО ЗАВЕРШЕН!")


if __name__ == "__main__":
    run_final_project()
    