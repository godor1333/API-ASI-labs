import React, { useState } from 'react';
import './styles/App.css';
import Dashboard from './components/Dashboard';
import Voting from './components/Voting';
import InvestmentMap from './components/InvestmentMap';
import Withdrawal from './components/Withdrawal';
import Login from './components/Login';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [user, setUser] = useState(null);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const renderView = () => {
    if (!user) {
      return <Login onLogin={handleLogin} />;
    }

    switch (currentView) {
      case 'dashboard':
        return <Dashboard />;
      case 'voting':
        return <Voting />;
      case 'map':
        return <InvestmentMap />;
      case 'withdrawal':
        return <Withdrawal />;
      default:
        return <Dashboard />;
    }
  };

  if (!user) {
    return (
      <div className="App">
        {renderView()}
      </div>
    );
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>🐝 BeeHive Investment Platform</h1>
        <div className="user-info">
          <span>Welcome, {user.username}</span>
          <span>Rating: {user.bee_rating} ⭐</span>
        </div>
        <nav>
          <button onClick={() => setCurrentView('dashboard')}>Dashboard</button>
          <button onClick={() => setCurrentView('voting')}>Voting</button>
          <button onClick={() => setCurrentView('map')}>Investment Map</button>
          <button onClick={() => setCurrentView('withdrawal')}>Withdraw</button>
          <button onClick={() => setUser(null)}>Logout</button>
        </nav>
      </header>
      <main>
        {renderView()}
      </main>
    </div>
  );
}

export default App;