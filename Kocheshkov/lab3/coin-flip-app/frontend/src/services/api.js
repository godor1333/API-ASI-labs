import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Интерцептор для добавления JWT токена
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const originalRequest = error.config;
    
    // Если ошибка 401 (неавторизован) и это не повторный запрос
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Удаляем невалидный токен
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Перенаправляем на страницу логина
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  register: (username, email, password) => api.post('/auth/register', { username, email, password }),
  test: () => api.get('/auth/test'),
};

export const gameAPI = {
  flip: (amount, chosenSide) => api.post('/game/flip', { amount, chosenSide }),
  quickBet: (amount, chosenSide) => api.post('/game/quick-bet', { amount, chosenSide }),
  getHistory: (limit, offset) => api.get(`/game/history?limit=${limit}&offset=${offset}`),
};

export const leaderboardAPI = {
  getLeaderboard: (limit) => api.get(`/leaderboard?limit=${limit}`),
};

export default api;