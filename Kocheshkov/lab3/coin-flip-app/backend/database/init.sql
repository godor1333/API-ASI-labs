-- Создание базы данных (если не существует)
SELECT 'CREATE DATABASE coin_flip'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'coin_flip')\gexec

-- Подключение к базе данных
\c coin_flip;

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    balance DECIMAL(15,2) DEFAULT 1000.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица ставок
CREATE TABLE IF NOT EXISTS bets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount DECIMAL(15,2) NOT NULL,
    chosen_side VARCHAR(10) CHECK (chosen_side IN ('heads', 'tails')),
    result VARCHAR(10) CHECK (result IN ('heads', 'tails')),
    win BOOLEAN,
    payout DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Материализованное представление для лидерборда
CREATE MATERIALIZED VIEW IF NOT EXISTS leaderboard AS
SELECT 
    u.id,
    u.username,
    u.balance,
    COUNT(b.id) as games_played,
    COUNT(CASE WHEN b.win = true THEN 1 END) as wins
FROM users u
LEFT JOIN bets b ON u.id = b.user_id
GROUP BY u.id, u.username, u.balance
ORDER BY u.balance DESC;

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_bets_user_id ON bets(user_id);
CREATE INDEX IF NOT EXISTS idx_bets_created_at ON bets(created_at);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Функция для обновления лидерборда
CREATE OR REPLACE FUNCTION refresh_leaderboard()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW leaderboard;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Триггеры для обновления лидерборда (убираем IF EXISTS для совместимости)
DROP TRIGGER IF EXISTS refresh_leaderboard_after_user ON users;
CREATE TRIGGER refresh_leaderboard_after_user
    AFTER UPDATE OF balance ON users
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_leaderboard();

DROP TRIGGER IF EXISTS refresh_leaderboard_after_bet ON bets;
CREATE TRIGGER refresh_leaderboard_after_bet
    AFTER INSERT ON bets
    FOR EACH STATEMENT
    EXECUTE FUNCTION refresh_leaderboard();

-- Инициализируем лидерборд
REFRESH MATERIALIZED VIEW leaderboard;