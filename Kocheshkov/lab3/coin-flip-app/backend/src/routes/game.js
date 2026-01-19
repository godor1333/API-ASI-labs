const express = require('express');
const db = require('../config/database');
const { authenticateToken } = require('../middleware/auth');
const router = express.Router();

// Сделать ставку
router.post('/flip', authenticateToken, async (req, res) => {
  let transactionCompleted = false;
  
  try {
    const { amount, chosenSide } = req.body;
    const userId = req.user.id;

    // Валидация
    if (!amount || amount <= 0) {
      return res.status(400).json({ error: 'Неверная сумма ставки' });
    }

    if (!['heads', 'tails'].includes(chosenSide)) {
      return res.status(400).json({ error: 'Неверная сторона монеты' });
    }

    // Начало транзакции
    await db.query('BEGIN');

    try {
      // Блокируем строку пользователя для чтения
      const userResult = await db.query(
        'SELECT balance FROM users WHERE id = $1 FOR UPDATE',
        [userId]
      );

      const currentBalance = parseFloat(userResult.rows[0].balance);

      if (currentBalance < amount) {
        await db.query('ROLLBACK');
        return res.status(400).json({ error: 'Недостаточно средств' });
      }

      // Симуляция подбрасывания монеты
      const result = Math.random() < 0.5 ? 'heads' : 'tails';
      const win = chosenSide === result;
      
      // РАСЧЕТ БАЛАНСА
      let newBalance;
      let payout;

      if (win) {
        payout = amount * 2;
        newBalance = currentBalance + amount;
      } else {
        payout = 0;
        newBalance = currentBalance - amount;
      }

      // Обновление баланса пользователя
      const updateResult = await db.query(
        'UPDATE users SET balance = $1 WHERE id = $2 RETURNING balance',
        [newBalance, userId]
      );

      const updatedBalance = parseFloat(updateResult.rows[0].balance);

      // Запись ставки
      const betResult = await db.query(
        `INSERT INTO bets (user_id, amount, chosen_side, result, win, payout) 
         VALUES ($1, $2, $3, $4, $5, $6) 
         RETURNING *`,
        [userId, amount, chosenSide, result, win, payout]
      );

      await db.query('COMMIT');
      transactionCompleted = true;

      // Получаем финальный баланс для проверки
      const finalCheck = await db.query(
        'SELECT balance FROM users WHERE id = $1',
        [userId]
      );
      const finalBalance = parseFloat(finalCheck.rows[0].balance);

      // Отправляем ответ
      const responseData = {
        result,
        win,
        payout,
        newBalance: finalBalance,
        bet: betResult.rows[0]
      };

      res.json(responseData);

    } catch (error) {
      if (!transactionCompleted) {
        await db.query('ROLLBACK');
      }
      throw error;
    }

  } catch (error) {
    console.error('Ошибка при выполнении ставки:', error);
    res.status(500).json({ error: 'Ошибка при выполнении ставки' });
  }
});

// Быстрые ставки
router.post('/quick-bet', authenticateToken, async (req, res) => {
  let transactionCompleted = false;
  
  try {
    const { amount, chosenSide } = req.body;
    const userId = req.user.id;

    // Начало транзакции
    await db.query('BEGIN');

    try {
      // Блокируем строку пользователя для чтения
      const userResult = await db.query(
        'SELECT balance FROM users WHERE id = $1 FOR UPDATE',
        [userId]
      );

      const currentBalance = parseFloat(userResult.rows[0].balance);

      if (currentBalance < amount) {
        await db.query('ROLLBACK');
        return res.status(400).json({ error: 'Недостаточно средств' });
      }

      // Симуляция подбрасывания монеты
      const result = Math.random() < 0.5 ? 'heads' : 'tails';
      const win = chosenSide === result;
      
      // РАСЧЕТ БАЛАНСА
      let newBalance;
      let payout;

      if (win) {
        payout = amount * 2;
        newBalance = currentBalance + amount;
      } else {
        payout = 0;
        newBalance = currentBalance - amount;
      }

      // Обновление баланса пользователя
      const updateResult = await db.query(
        'UPDATE users SET balance = $1 WHERE id = $2 RETURNING balance',
        [newBalance, userId]
      );

      const updatedBalance = parseFloat(updateResult.rows[0].balance);

      // Запись ставки
      await db.query(
        `INSERT INTO bets (user_id, amount, chosen_side, result, win, payout) 
         VALUES ($1, $2, $3, $4, $5, $6)`,
        [userId, amount, chosenSide, result, win, payout]
      );

      await db.query('COMMIT');
      transactionCompleted = true;

      // Получаем финальный баланс для проверки
      const finalCheck = await db.query(
        'SELECT balance FROM users WHERE id = $1',
        [userId]
      );
      const finalBalance = parseFloat(finalCheck.rows[0].balance);

      const responseData = {
        result,
        win,
        payout,
        newBalance: finalBalance
      };

      res.json(responseData);

    } catch (error) {
      if (!transactionCompleted) {
        await db.query('ROLLBACK');
      }
      throw error;
    }

  } catch (error) {
    console.error('Ошибка при быстрой ставке:', error);
    res.status(500).json({ error: 'Ошибка при быстрой ставке' });
  }
});

// История ставок
router.get('/history', authenticateToken, async (req, res) => {
  try {
    const { limit = 10, offset = 0 } = req.query;
    const userId = req.user.id;

    const result = await db.query(
      `SELECT * FROM bets 
       WHERE user_id = $1 
       ORDER BY created_at DESC 
       LIMIT $2 OFFSET $3`,
      [userId, limit, offset]
    );

    const totalResult = await db.query(
      'SELECT COUNT(*) FROM bets WHERE user_id = $1',
      [userId]
    );

    res.json({
      bets: result.rows,
      total: parseInt(totalResult.rows[0].count)
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Ошибка при получении истории' });
  }
});

module.exports = router;