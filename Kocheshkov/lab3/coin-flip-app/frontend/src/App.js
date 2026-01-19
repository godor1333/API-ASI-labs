import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { isAuthenticated, validateToken } from './utils/auth';
import Login from './pages/Login';
import Register from './pages/Register';
import Game from './pages/Game';
import Profile from './pages/Profile';
import Leaderboard from './components/Leaderboard';
import Navigation from './components/Navigation';
import './App.css';

const App = () => {
  const [authChecked, setAuthChecked] = useState(false);
  const [isAuth, setIsAuth] = useState(false);

  useEffect(() => {
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    try {
      const authenticated = await validateToken();
      setIsAuth(authenticated);
    } catch (error) {
      console.error('Ошибка проверки аутентификации:', error);
      setIsAuth(false);
    } finally {
      setAuthChecked(true);
    }
  };

  // Защищенный маршрут
  const ProtectedRoute = ({ children }) => {
    if (!authChecked) {
      return <div className="loading">Проверка авторизации...</div>;
    }
    return isAuth ? children : <Navigate to="/login" />;
  };

  // Публичный маршрут (только для неавторизованных)
  const PublicRoute = ({ children }) => {
    if (!authChecked) {
      return <div className="loading">Проверка авторизации...</div>;
    }
    return !isAuth ? children : <Navigate to="/game" />;
  };

  if (!authChecked) {
    return (
      <div className="app-loading">
        <div className="loading-spinner"></div>
        <p>Загрузка приложения...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        {isAuth && <Navigation />}
        <main className="main-content">
          <Routes>
            <Route path="/login" element={
              <PublicRoute>
                <Login onLogin={() => setIsAuth(true)} />
              </PublicRoute>
            } />
            <Route path="/register" element={
              <PublicRoute>
                <Register onRegister={() => setIsAuth(true)} />
              </PublicRoute>
            } />
            <Route path="/game" element={
              <ProtectedRoute>
                <Game />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } />
            <Route path="/leaderboard" element={
              <ProtectedRoute>
                <div className="page-container">
                  <h1>Топ игроков</h1>
                  <Leaderboard />
                </div>
              </ProtectedRoute>
            } />
            <Route path="/" element={<Navigate to="/game" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;