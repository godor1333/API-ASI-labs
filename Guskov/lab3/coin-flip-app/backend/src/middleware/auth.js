const jwt = require('jsonwebtoken');
const db = require('../config/database');

const authenticateToken = async (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Токен доступа отсутствует' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'your-super-secret-jwt-key-here');
    
    // Проверяем существование пользователя
    const result = await db.query(
      'SELECT id, username, email, balance FROM users WHERE id = $1', 
      [decoded.userId]
    );
    
    if (result.rows.length === 0) {
      return res.status(401).json({ error: 'Пользователь не найден' });
    }

    req.user = result.rows[0];
    next();
  } catch (error) {
    console.error('❌ Ошибка проверки токена:', error.message);
    
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Токен истек' });
    } else if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ error: 'Неверный токен' });
    } else {
      return res.status(500).json({ error: 'Ошибка аутентификации' });
    }
  }
};

module.exports = { authenticateToken };