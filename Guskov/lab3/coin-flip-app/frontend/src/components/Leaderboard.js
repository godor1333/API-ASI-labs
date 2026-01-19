import React, { useState, useEffect } from 'react';
import { leaderboardAPI } from '../services/api';
import './Leaderboard.css';

const Leaderboard = ({ refreshTrigger }) => {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadLeaderboard = async () => {
    try {
      setLoading(true);
      const response = await leaderboardAPI.getLeaderboard(20);
      setLeaderboard(response.data);
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Ошибка загрузки лидерборда:', error);
    } finally {
      setLoading(false);
    }
  };

  // Загружаем при монтировании
  useEffect(() => {
    loadLeaderboard();
  }, []);

  // Обновляем при получении триггера
  useEffect(() => {
    if (refreshTrigger) {
      loadLeaderboard();
    }
  }, [refreshTrigger]);

  if (loading) return <div className="loading">Загрузка лидерборда...</div>;

  return (
    <div className="leaderboard-container">
      <div className="leaderboard-header">
        <h2>🏆 Топ игроков</h2>
        {lastUpdated && (
          <div className="last-updated">
            Обновлено: {lastUpdated.toLocaleTimeString()}
          </div>
        )}
        <button 
          className="refresh-btn"
          onClick={loadLeaderboard}
          disabled={loading}
        >
          🔄 Обновить
        </button>
      </div>
      
      <div className="leaderboard">
        {leaderboard.map((player, index) => (
          <div key={player.id} className="leaderboard-item">
            <span className="rank">
              {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
            </span>
            <span className="username">{player.username}</span>
            <span className="balance">${player.balance}</span>
            <span className="stats">
              🎮 {player.games_played} | ✅ {player.wins || 0}
            </span>
          </div>
        ))}
        
        {leaderboard.length === 0 && (
          <div className="no-players">
            Пока нет игроков в таблице лидеров
          </div>
        )}
      </div>
    </div>
  );
};

export default Leaderboard;