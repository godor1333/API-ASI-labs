const express = require('express');
const db = require('../config/database');
const router = express.Router();

// Топ игроков
router.get('/', async (req, res) => {
  try {
    const { limit = 10 } = req.query;

    const result = await db.query(
      `SELECT * FROM leaderboard 
       ORDER BY balance DESC 
       LIMIT $1`,
      [limit]
    );

    res.json(result.rows);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Ошибка при получении таблицы лидеров' });
  }
});

module.exports = router;