import gymnasium as gym

# Проверим все среды
print("🔍 Проверка установленных Atari сред...")
all_envs = list(gym.envs.registry)

# Найдем все Atari игры
atari_envs = []
for env_id in all_envs:
    if 'ALE/' in env_id or any(x in env_id.lower() for x in ['space', 'invader', 'breakout', 'pong']):
        atari_envs.append(env_id)

print(f"\n📊 Найдено {len(atari_envs)} Atari сред:")

# Группируем по играм
games = {}
for env_id in sorted(atari_envs):
    game_name = env_id.split('/')[-1].split('-')[0]
    if game_name not in games:
        games[game_name] = []
    games[game_name].append(env_id)

# Выводим
for game in sorted(games.keys()):
    print(f"\n🎮 {game}:")
    for env_id in games[game]:
        print(f"  - {env_id}")

# Тест Space Invaders
print("\n🎯 Тестируем Space Invaders...")
test_envs = [
    "SpaceInvaders-v0",
    "SpaceInvaders-v4", 
    "SpaceInvadersNoFrameskip-v4",
    "ALE/SpaceInvaders-v5"
]

for env_id in test_envs:
    try:
        env = gym.make(env_id, render_mode='rgb_array')
        obs, _ = env.reset()
        print(f"  ✅ {env_id}: работает! Размер: {obs.shape}")
        env.close()
    except Exception as e:
        print(f"  ❌ {env_id}: {e}")