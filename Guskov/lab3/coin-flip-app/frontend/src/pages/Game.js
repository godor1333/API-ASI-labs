import React, { useState } from 'react';
import CoinFlip from '../components/CoinFlip';
import Leaderboard from '../components/Leaderboard';
import './Game.css';

const Game = () => {
  const [refreshLeaderboard, setRefreshLeaderboard] = useState(0);

  const handleBetComplete = () => {
    // Увеличиваем счетчик для принудительного обновления лидерборда
    setRefreshLeaderboard(prev => prev + 1);
  };

  return (
    <div className="game-page">
      <div className="game-container">
        <div className="game-area">
          <CoinFlip onBetComplete={handleBetComplete} />
        </div>
        <div className="sidebar">
          <Leaderboard refreshTrigger={refreshLeaderboard} />
        </div>
      </div>
    </div>
  );
};

export default Game;