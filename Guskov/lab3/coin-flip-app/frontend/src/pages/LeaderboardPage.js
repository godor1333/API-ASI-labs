import React from 'react';
import Leaderboard from '../components/Leaderboard';
import './LeaderboardPage.css';

const LeaderboardPage = () => {
  return (
    <div className="leaderboard-page">
      <div className="container">
        <h1>Таблица лидеров</h1>
        <Leaderboard />
      </div>
    </div>
  );
};

export default LeaderboardPage;