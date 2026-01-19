const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const db = require('./config/database'); // ← Импортируем правильно
require('dotenv').config();

const authRoutes = require('./routes/auth');
const gameRoutes = require('./routes/game');
const leaderboardRoutes = require('./routes/leaderboard');

const app = express();
const PORT = process.env.PORT || 3000;

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
});

app.use(cors());
app.use(limiter);
app.use(express.json());

// Простой health check
app.get('/health', async (req, res) => {
  try {
    // Простая проверка подключения к БД
    await db.query('SELECT 1');
    res.json({ 
      status: 'OK', 
      message: 'Сервер и база данных работают'
    });
  } catch (error) {
    res.status(500).json({ 
      status: 'ERROR', 
      message: 'Проблемы с базой данных',
      error: error.message 
    });
  }
});

// Простой тест таблиц
app.get('/api/test-db', async (req, res) => {
  try {
    const result = await db.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public'
      AND table_type = 'BASE TABLE'
    `);
    
    res.json({ 
      tables: result.rows.map(row => row.table_name),
      message: 'Проверка таблиц выполнена'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Подключаем маршруты
app.use('/api/auth', authRoutes);
app.use('/api/game', gameRoutes);
app.use('/api/leaderboard', leaderboardRoutes);

// Обработка 404
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Маршрут не найден' });
});

// Обработка ошибок
app.use((err, req, res, next) => {
  console.error('Ошибка сервера:', err);
  res.status(500).json({ 
    error: 'Внутренняя ошибка сервера'
  });
});

// Функция для ожидания базы данных (упрощенная)
const waitForDatabase = async (maxAttempts = 10) => {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    console.log(`🔄 Попытка подключения к БД (${attempt}/${maxAttempts})...`);
    
    try {
      await db.query('SELECT 1');
      console.log('✅ База данных готова');
      return true;
    } catch (error) {
      console.log(`❌ Попытка ${attempt} не удалась:`, error.message);
      
      if (attempt < maxAttempts) {
        console.log('⏳ Ожидание 3 секунды перед следующей попыткой...');
        await new Promise(resolve => setTimeout(resolve, 3000));
      }
    }
  }
  
  throw new Error('Не удалось подключиться к базе данных после всех попыток');
};

// Запуск сервера
const initDatabase = require('./init-db');

// В функции startServer после подключения к БД:
const startServer = async () => {
  try {
    console.log('🔄 Запуск сервера...');
    
    // Ждем базу данных
    await waitForDatabase();
    
    // Инициализируем таблицы
    await initDatabase();
    
    app.listen(PORT, () => {
      console.log(`🚀 Сервер запущен на порту ${PORT}`);
    });
  } catch (error) {
    console.error('❌ Не удалось запустить сервер:', error.message);
    process.exit(1);
  }
};

startServer();