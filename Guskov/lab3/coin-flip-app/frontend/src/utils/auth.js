// Сохранение токена и данных пользователя
export const setAuth = (token, user) => {
  try {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    console.log('✅ Токен сохранен:', token ? 'да' : 'нет');
  } catch (error) {
    console.error('❌ Ошибка сохранения токена:', error);
  }
};

// Получение данных пользователя
export const getCurrentUser = () => {
  try {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  } catch (error) {
    console.error('❌ Ошибка получения пользователя:', error);
    return null;
  }
};

// Получение токена
export const getToken = () => {
  try {
    return localStorage.getItem('token');
  } catch (error) {
    console.error('❌ Ошибка получения токена:', error);
    return null;
  }
};

// Выход
export const logout = () => {
  try {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    console.log('✅ Выход выполнен');
  } catch (error) {
    console.error('❌ Ошибка выхода:', error);
  }
};

// Проверка авторизации
export const isAuthenticated = () => {
  const token = getToken();
  if (!token) return false;

  try {
    // Базовая проверка JWT токена (без верификации подписи)
    const payload = JSON.parse(atob(token.split('.')[1]));
    const isExpired = payload.exp * 1000 < Date.now();
    
    if (isExpired) {
      logout();
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('❌ Ошибка проверки токена:', error);
    logout();
    return false;
  }
};

// Проверка валидности токена
export const validateToken = async () => {
  const token = getToken();
  if (!token) return false;

  try {
    // Можно добавить запрос к серверу для проверки токена
    // const response = await api.get('/auth/validate');
    // return response.status === 200;
    return isAuthenticated();
  } catch (error) {
    console.error('❌ Ошибка валидации токена:', error);
    return false;
  }
};