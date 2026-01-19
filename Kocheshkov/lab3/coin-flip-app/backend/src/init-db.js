const db = require('./config/database');

const initDatabase = async () => {
  try {
    console.log('🔄 Инициализация базы данных...');
    
    // Создаем таблицу users
    await db.query(`
      CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        balance DECIMAL(15,2) DEFAULT 1000.00,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    console.log('✅ Таблица users создана');
    
    // Создаем таблицу bets
    await db.query(`
      CREATE TABLE IF NOT EXISTS bets (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        amount DECIMAL(15,2) NOT NULL,
        chosen_side VARCHAR(10) CHECK (chosen_side IN ('heads', 'tails')),
        result VARCHAR(10) CHECK (result IN ('heads', 'tails')),
        win BOOLEAN,
        payout DECIMAL(15,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);
    console.log('✅ Таблица bets создана');
    
    // Создаем индексы
    await db.query('CREATE INDEX IF NOT EXISTS idx_bets_user_id ON bets(user_id)');
    await db.query('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)');
    console.log('✅ Индексы созданы');
    
    console.log('🎉 База данных успешно инициализирована');
  } catch (error) {
    console.error('❌ Ошибка инициализации базы данных:', error);
  }
};

// Запускаем инициализацию если файл вызван напрямую
if (require.main === module) {
  initDatabase();
}

module.exports = initDatabase;