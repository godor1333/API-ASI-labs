import React, { useState, useEffect } from 'react';
import { gameAPI } from '../services/api';
import { getCurrentUser } from '../utils/auth';
import './CoinFlip.css';

const CoinFlip = ({ onBetComplete }) => {
  const [isFlipping, setIsFlipping] = useState(false);
  const [result, setResult] = useState(null);
  const [betAmount, setBetAmount] = useState(10);
  const [chosenSide, setChosenSide] = useState('heads');
  const [user, setUser] = useState(getCurrentUser());
  const [quickBetMode, setQuickBetMode] = useState(false);
  const [currentSide, setCurrentSide] = useState('heads');

  const quickBets = [10, 25, 50, 100];

  useEffect(() => {
    const currentUser = getCurrentUser();
    setUser(currentUser);
  }, []);

  const flipCoin = async (specificAmount = null) => {
    if (isFlipping) return;

    const actualAmount = specificAmount !== null ? specificAmount : betAmount;
    
    setIsFlipping(true);
    setResult(null);
    setCurrentSide(chosenSide);

    try {
      const apiCall = quickBetMode ? gameAPI.quickBet : gameAPI.flip;
      const response = await apiCall(actualAmount, chosenSide);
      
      setTimeout(() => {
        const resultData = response.data;
        setResult(resultData);
        setCurrentSide(resultData.result);
        
        const updatedUser = { 
          ...user, 
          balance: resultData.newBalance 
        };
        
        setUser(updatedUser);
        localStorage.setItem('user', JSON.stringify(updatedUser));
        
        if (onBetComplete) {
          onBetComplete();
        }
        
        setIsFlipping(false);
      }, 2000);
      
    } catch (error) {
      alert(error.response?.data?.error || 'Ошибка при выполнении ставки');
      setIsFlipping(false);
    }
  };

  const handleQuickBetClick = (amount) => {
    setBetAmount(amount);
    
    if (quickBetMode) {
      setTimeout(() => {
        flipCoin(amount);
      }, 100);
    }
  };

  const handleManualBetChange = (amount) => {
    setBetAmount(amount);
  };

  const handleSideChange = (side) => {
    setChosenSide(side);
  };

  const handleFlipButtonClick = () => {
    flipCoin();
  };

  const getSideName = (side) => {
    return side === 'heads' ? 'Орла 🦅' : 'Решки 1';
  };

  return (
    <div className="coin-flip-container">
      <div className="user-info">
        <h2>💰 Баланс: ${user?.balance || 0}</h2>
      </div>

      <div className="game-controls">
        <div className="bet-amount">
          <label>Сумма ставки:</label>
          <input
            type="number"
            value={betAmount}
            onChange={(e) => handleManualBetChange(Number(e.target.value))}
            min="1"
            max={user?.balance || 0}
            disabled={isFlipping}
          />
        </div>

        <div className="side-selection">
          <button
            className={chosenSide === 'heads' ? 'active' : ''}
            onClick={() => handleSideChange('heads')}
            disabled={isFlipping}
          >
            🦅 Орел
          </button>
          <button
            className={chosenSide === 'tails' ? 'active' : ''}
            onClick={() => handleSideChange('tails')}
            disabled={isFlipping}
          >
            1 Решка
          </button>
        </div>

        <div className="mode-selection">
          <label>
            <input
              type="checkbox"
              checked={quickBetMode}
              onChange={(e) => setQuickBetMode(e.target.checked)}
              disabled={isFlipping}
            />
            Быстрая ставка
          </label>
          <div className="mode-hint">
            {quickBetMode 
              ? "✅ Ставки начинаются сразу при выборе суммы" 
              : "❌ Ставки требуют нажатия кнопки 'Поставить'"
            }
          </div>
        </div>
      </div>

      <div className="quick-bets">
        {quickBets.map(amount => (
          <button
            key={amount}
            className="quick-bet-btn"
            onClick={() => handleQuickBetClick(amount)}
            disabled={isFlipping || amount > (user?.balance || 0)}
          >
            ${amount}
          </button>
        ))}
      </div>

      <div className="coin-container">
        <div className={`coin ${isFlipping ? 'flipping' : ''} ${currentSide}`}>
          <div className="coin-front"></div>
          <div className="coin-back"></div>
        </div>
      </div>

      {!isFlipping && !result && (
        <div className="bet-info">
          <p>Ставка: <strong>${betAmount}</strong> на <strong>{getSideName(chosenSide)}</strong></p>
          <p>Текущий баланс: <strong>${user?.balance || 0}</strong></p>
          {!quickBetMode && (
            <p className="instruction">👉 Нажмите кнопку "Поставить" чтобы сделать ставку</p>
          )}
          {quickBetMode && (
            <p className="instruction">⚡ Быстрая ставка активна - игра начнется автоматически при выборе суммы</p>
          )}
        </div>
      )}

      {!quickBetMode && (
        <button
          className="flip-button"
          onClick={handleFlipButtonClick}
          disabled={isFlipping || betAmount > (user?.balance || 0) || betAmount <= 0}
        >
          {isFlipping ? '🔄 Монета летит...' : `🎯 Поставить $${betAmount}`}
        </button>
      )}

      {quickBetMode && !isFlipping && !result && (
        <div className="quick-mode-message">
          <p>⚡ Выберите сумму ставки для начала игры</p>
          <p style={{ fontSize: '14px', marginTop: '5px', opacity: '0.8' }}>
            Текущая ставка: <strong>${betAmount}</strong> | Сторона: <strong>{getSideName(chosenSide)}</strong>
          </p>
        </div>
      )}

      {result && !isFlipping && (
        <div className={`result ${result.win ? 'win' : 'lose'}`}>
          <h3>{result.win ? '🎉 ПОБЕДА!' : '💸 ПРОИГРЫШ'}</h3>
          <p>Вы загадали: <strong>{getSideName(chosenSide)}</strong></p>
          <p>Выпало: <strong>{getSideName(result.result)}</strong></p>
          <p className="result-amount">
            {result.win ? `💰 +$${result.payout}` : `💸 -$${betAmount}`}
          </p>
          <p className="new-balance">Новый баланс: <strong>${result.newBalance}</strong></p>
        </div>
      )}
    </div>
  );
};

export default CoinFlip;