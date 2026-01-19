const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'db',
  database: process.env.DB_NAME || 'coin_flip',
  password: process.env.DB_PASSWORD || 'password',
  port: process.env.DB_PORT || 5432,
  connectionTimeoutMillis: 5000,
  idleTimeoutMillis: 30000,
  max: 20,
});

// Тестируем подключение при старте
pool.on('connect', () => {
  console.log('✅ Подключение к PostgreSQL установлено');
});

pool.on('error', (err) => {
  console.error('❌ Ошибка подключения к PostgreSQL:', err);
});

// Функция для проверки подключения
const testConnection = async () => {
  try {
    const client = await pool.connect();
    console.log('✅ База данных доступна');
    client.release();
    return true;
  } catch (error) {
    console.error('❌ Ошибка подключения к базе:', error.message);
    return false;
  }
};

module.exports = {
  query: (text, params) => pool.query(text, params),
  pool,
  testConnection  // ← ДОБАВЛЯЕМ ЭТУ СТРОКУ!
};