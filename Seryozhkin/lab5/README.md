# Аналитика RL-агентов в Minecraft (MineRL + BASALT)

Платформа для запуска, анализа и сравнения reinforcement learning агентов в Minecraft с использованием сред MineRL и бенчмарка BASALT. Фокус — на «размытых» (human-like) задачах без чёткой reward-функции.

## Возможности

- Запуск RL-агентов (PPO, DQN, IMPALA, JueWu-MC, DIP-RL и др.) в среде MineRL/BASALT
- Анализ траекторий: состояния, действия, награды, embeddings
- Оценка с помощью RL-friendly VLM (CLIP4MC / CLIP-подобные модели)
- Сравнение с человеческими демонстрациями из MineRL/BEDD/BASALT
- Визуализация: графики reward vs steps, траектории, sample efficiency, overfitting на "тупые" паттерны
- Дашборд экспериментов: история запусков, мониторинг GPU/CPU, логи, метрики

## Установка

### 1. Установите зависимости Python

```bash
pip install -r requirements.txt