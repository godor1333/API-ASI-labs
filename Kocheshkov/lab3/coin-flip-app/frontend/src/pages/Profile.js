import React, { useState, useEffect } from 'react';
import { gameAPI } from '../services/api';
import { getCurrentUser } from '../utils/auth';

const Profile = () => {
  const [user] = useState(getCurrentUser());
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await gameAPI.getHistory(10, 0);
      setHistory(response.data.bets);
    } catch (error) {
      console.error('Ошибка загрузки истории:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Загрузка...</div>;

  return (
    <div className="profile-page">
      <h2>Профиль игрока</h2>
      <div className="profile-info">
        <p><strong>Имя пользователя:</strong> {user?.username}</p>
        <p><strong>Email:</strong> {user?.email}</p>
        <p><strong>Баланс:</strong> ${user?.balance}</p>
      </div>
      
      <div className="bet-history">
        <h3>Последние ставки</h3>
        {history.length === 0 ? (
          <p>Ставок пока нет</p>
        ) : (
          <div className="history-list">
            {history.map(bet => (
              <div key={bet.id} className={`history-item ${bet.win ? 'win' : 'lose'}`}>
                <span>${bet.amount} на {bet.chosen_side}</span>
                <span>Результат: {bet.result}</span>
                <span>{bet.win ? `+$${bet.payout}` : `-$${bet.amount}`}</span>
                <span>{new Date(bet.created_at).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;