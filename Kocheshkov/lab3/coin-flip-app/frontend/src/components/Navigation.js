import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { logout, getCurrentUser } from '../utils/auth';
import './Navigation.css';

const Navigation = () => {
  const navigate = useNavigate();
  const user = getCurrentUser();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <Link to="/game">Coin Flip</Link>
      </div>
      <div className="nav-links">
        <Link to="/game">Игра</Link>
        <Link to="/leaderboard">Топ игроков</Link>
        <Link to="/profile">Профиль</Link>
      </div>
      <div className="nav-user">
        <span>Привет, {user?.username}!</span>
        <button onClick={handleLogout}>Выйти</button>
      </div>
    </nav>
  );
};

export default Navigation;