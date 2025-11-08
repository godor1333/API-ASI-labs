const API_URL = '/api';

let currentToken = localStorage.getItem('token');
let currentUser = null;
let currentView = 'plants';
let currentPlantId = null;

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
    if (currentToken) {
        checkAuth();
    } else {
        showAuth();
    }
    
    setupEventListeners();
});

// Проверка авторизации
async function checkAuth() {
    try {
        const response = await fetch(`${API_URL}/users/me`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            showMain();
        } else {
            localStorage.removeItem('token');
            currentToken = null;
            showAuth();
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        showAuth();
    }
}

// Показать форму авторизации
function showAuth() {
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('main-section').style.display = 'none';
    document.getElementById('logout-btn').style.display = 'none';
}

// Показать основное приложение
function showMain() {
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('main-section').style.display = 'flex';
    document.getElementById('logout-btn').style.display = 'block';
    document.getElementById('username-display').textContent = currentUser.username;
    loadPlants();
}

// Настройка обработчиков событий
function setupEventListeners() {
    // Табы авторизации
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tab = e.target.dataset.tab;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            
            e.target.classList.add('active');
            document.getElementById(`${tab}-form`).classList.add('active');
        });
    });
    
    // Формы авторизации
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    
    // Выход
    document.getElementById('logout-btn').addEventListener('click', () => {
        localStorage.removeItem('token');
        currentToken = null;
        showAuth();
    });
    
    // Боковая панель
    document.querySelectorAll('.sidebar-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const view = e.target.dataset.view;
            switchView(view);
        });
    });
    
    // Форма добавления растения
    document.getElementById('add-plant-form').addEventListener('submit', handleAddPlant);
    
    // Кнопка назад
    document.getElementById('back-btn').addEventListener('click', () => {
        switchView('plants');
    });
}

// Вход
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    try {
        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            currentToken = data.access_token;
            localStorage.setItem('token', currentToken);
            await checkAuth();
        } else {
            showError('Неверное имя пользователя или пароль');
        }
    } catch (error) {
        showError('Ошибка подключения к серверу');
    }
}

// Регистрация
async function handleRegister(e) {
    e.preventDefault();
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });
        
        if (response.ok) {
            showNotification('Регистрация успешна! Войдите в систему.');
            document.querySelector('.tab-btn[data-tab="login"]').click();
        } else {
            const error = await response.json();
            showError(error.detail || 'Ошибка регистрации');
        }
    } catch (error) {
        showError('Ошибка подключения к серверу');
    }
}

// Показать ошибку
function showError(message) {
    const errorDiv = document.getElementById('auth-error');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
    setTimeout(() => errorDiv.classList.remove('show'), 5000);
}

// Показать уведомление
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Переключение вида
function switchView(view) {
    currentView = view;
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.querySelectorAll('.sidebar-btn').forEach(b => b.classList.remove('active'));
    
    if (view === 'plants') {
        document.getElementById('plants-view').classList.add('active');
        document.querySelector('.sidebar-btn[data-view="plants"]').classList.add('active');
        loadPlants();
    } else if (view === 'add-plant') {
        document.getElementById('add-plant-view').classList.add('active');
        document.querySelector('.sidebar-btn[data-view="add-plant"]').classList.add('active');
    } else if (view === 'reminders') {
        document.getElementById('reminders-view').classList.add('active');
        document.querySelector('.sidebar-btn[data-view="reminders"]').classList.add('active');
        loadReminders();
    } else if (view === 'plant-detail') {
        document.getElementById('plant-detail-view').classList.add('active');
    }
}

// Загрузка растений
async function loadPlants() {
    try {
        const response = await fetch(`${API_URL}/plants`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const plants = await response.json();
            displayPlants(plants);
        }
    } catch (error) {
        console.error('Failed to load plants:', error);
    }
}

// Отображение растений
function displayPlants(plants) {
    const container = document.getElementById('plants-list');
    
    if (plants.length === 0) {
        container.innerHTML = '<p>У вас пока нет растений. Добавьте первое!</p>';
        return;
    }
    
    container.innerHTML = plants.map(plant => `
        <div class="plant-card" onclick="showPlantDetail(${plant.id})">
            <h3>${plant.name}</h3>
            ${plant.species ? `<div class="species">${plant.species}</div>` : ''}
            <div class="date">Добавлено: ${new Date(plant.planted_date).toLocaleDateString('ru-RU')}</div>
        </div>
    `).join('');
}

// Показать детали растения
async function showPlantDetail(plantId) {
    currentPlantId = plantId;
    switchView('plant-detail');
    
    try {
        const [plant, entries, photos, reminders] = await Promise.all([
            fetch(`${API_URL}/plants/${plantId}`, {
                headers: { 'Authorization': `Bearer ${currentToken}` }
            }).then(r => r.json()),
            fetch(`${API_URL}/plants/${plantId}/entries`, {
                headers: { 'Authorization': `Bearer ${currentToken}` }
            }).then(r => r.json()),
            fetch(`${API_URL}/plants/${plantId}/photos`, {
                headers: { 'Authorization': `Bearer ${currentToken}` }
            }).then(r => r.json()),
            fetch(`${API_URL}/plants/${plantId}/reminders`, {
                headers: { 'Authorization': `Bearer ${currentToken}` }
            }).then(r => r.json())
        ]);
        
        displayPlantDetail(plant, entries, photos, reminders);
    } catch (error) {
        console.error('Failed to load plant details:', error);
    }
}

// Отображение деталей растения
function displayPlantDetail(plant, entries, photos, reminders) {
    const container = document.getElementById('plant-detail-content');
    
    container.innerHTML = `
        <div class="plant-detail">
            <h2>${plant.name}</h2>
            <div class="meta">
                ${plant.species ? `<div>Вид: ${plant.species}</div>` : ''}
                <div>Добавлено: ${new Date(plant.planted_date).toLocaleDateString('ru-RU')}</div>
                ${plant.description ? `<div>${plant.description}</div>` : ''}
            </div>
            
            <div class="tabs-section">
                <div class="tabs">
                    <button class="tab-btn active" onclick="switchPlantTab('entries')">📝 Записи</button>
                    <button class="tab-btn" onclick="switchPlantTab('photos')">📷 Фото</button>
                    <button class="tab-btn" onclick="switchPlantTab('reminders')">🔔 Напоминания</button>
                </div>
                
                <div id="entries-tab" class="tab-content active">
                    <h3>Дневник ухода</h3>
                    <button class="btn-primary" onclick="showAddEntryForm()">Добавить запись</button>
                    <div id="entries-list" class="entries-list"></div>
                </div>
                
                <div id="photos-tab" class="tab-content">
                    <h3>Фото прогресса</h3>
                    <div class="file-upload">
                        <input type="file" id="photo-upload" accept="image/*">
                        <input type="text" id="photo-description" placeholder="Описание фото">
                        <button class="btn-primary" onclick="uploadPhoto()">Загрузить фото</button>
                    </div>
                    <div id="photos-gallery" class="photo-gallery"></div>
                </div>
                
                <div id="reminders-tab" class="tab-content">
                    <h3>Напоминания</h3>
                    <button class="btn-primary" onclick="showAddReminderForm()">Добавить напоминание</button>
                    <div id="reminders-list-detail"></div>
                </div>
            </div>
        </div>
    `;
    
    displayEntries(entries);
    displayPhotos(photos);
    displayRemindersDetail(reminders);
}

// Переключение вкладок деталей растения
window.switchPlantTab = function(tab) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    
    document.getElementById(`${tab}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// Отображение записей
function displayEntries(entries) {
    const container = document.getElementById('entries-list');
    
    if (entries.length === 0) {
        container.innerHTML = '<p>Пока нет записей</p>';
        return;
    }
    
    container.innerHTML = entries.map(entry => {
        const actions = [];
        if (entry.watering) actions.push('<span class="action-badge">💧 Полив</span>');
        if (entry.fertilizing) actions.push('<span class="action-badge">🌿 Удобрение</span>');
        if (entry.pruning) actions.push('<span class="action-badge">✂️ Обрезка</span>');
        if (entry.other_care) actions.push(`<span class="action-badge">${entry.other_care}</span>`);
        
        return `
            <div class="entry-card">
                <div class="date">${new Date(entry.entry_date).toLocaleString('ru-RU')}</div>
                ${entry.notes ? `<p>${entry.notes}</p>` : ''}
                ${actions.length > 0 ? `<div class="actions">${actions.join('')}</div>` : ''}
            </div>
        `;
    }).join('');
}

// Отображение фото
function displayPhotos(photos) {
    const container = document.getElementById('photos-gallery');
    
    if (photos.length === 0) {
        container.innerHTML = '<p>Пока нет фото</p>';
        return;
    }
    
    container.innerHTML = photos.map(photo => `
        <div class="photo-item">
            <img src="${photo.photo_path}" alt="${photo.description || ''}">
            ${photo.description ? `<div class="description">${photo.description}</div>` : ''}
        </div>
    `).join('');
}

// Отображение напоминаний в деталях
function displayRemindersDetail(reminders) {
    const container = document.getElementById('reminders-list-detail');
    
    if (reminders.length === 0) {
        container.innerHTML = '<p>Нет активных напоминаний</p>';
        return;
    }
    
    container.innerHTML = reminders.map(rem => `
        <div class="reminder-card">
            <h3>${rem.reminder_type}</h3>
            <div class="time">Следующее: ${new Date(rem.next_reminder).toLocaleString('ru-RU')}</div>
            <div class="time">Частота: каждые ${rem.frequency_days} дней</div>
            <div class="actions">
                <button class="btn-primary" onclick="completeReminder(${rem.id})">Выполнено</button>
            </div>
        </div>
    `).join('');
}

// Добавление растения
async function handleAddPlant(e) {
    e.preventDefault();
    const name = document.getElementById('plant-name').value;
    const species = document.getElementById('plant-species').value;
    const description = document.getElementById('plant-description').value;
    
    try {
        const response = await fetch(`${API_URL}/plants`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ name, species, description })
        });
        
        if (response.ok) {
            showNotification('Растение добавлено!');
            document.getElementById('add-plant-form').reset();
            switchView('plants');
        }
    } catch (error) {
        showNotification('Ошибка при добавлении растения');
    }
}

// Показать форму добавления записи
window.showAddEntryForm = function() {
    const form = prompt('Введите запись (формат: текст; полив; удобрение; обрезка; другое)');
    if (!form) return;
    
    const parts = form.split(';').map(s => s.trim());
    const entry = {
        notes: parts[0] || null,
        watering: parts[1]?.toLowerCase() === 'да' || parts[1]?.toLowerCase() === 'yes',
        fertilizing: parts[2]?.toLowerCase() === 'да' || parts[2]?.toLowerCase() === 'yes',
        pruning: parts[3]?.toLowerCase() === 'да' || parts[3]?.toLowerCase() === 'yes',
        other_care: parts[4] || null
    };
    
    addEntry(entry);
}

// Добавление записи
async function addEntry(entry) {
    try {
        const response = await fetch(`${API_URL}/plants/${currentPlantId}/entries`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify(entry)
        });
        
        if (response.ok) {
            showNotification('Запись добавлена!');
            showPlantDetail(currentPlantId);
        }
    } catch (error) {
        showNotification('Ошибка при добавлении записи');
    }
}

// Загрузка фото
window.uploadPhoto = async function() {
    const fileInput = document.getElementById('photo-upload');
    const description = document.getElementById('photo-description').value;
    
    if (!fileInput.files[0]) {
        showNotification('Выберите файл');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    if (description) {
        formData.append('description', description);
    }
    
    try {
        const response = await fetch(`${API_URL}/plants/${currentPlantId}/photos`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            },
            body: formData
        });
        
        if (response.ok) {
            showNotification('Фото загружено!');
            fileInput.value = '';
            document.getElementById('photo-description').value = '';
            showPlantDetail(currentPlantId);
        }
    } catch (error) {
        showNotification('Ошибка при загрузке фото');
    }
}

// Показать форму добавления напоминания
window.showAddReminderForm = function() {
    const type = prompt('Тип напоминания (полив, удобрение, обрезка и т.д.):');
    if (!type) return;
    
    const days = prompt('Частота (дней):');
    if (!days) return;
    
    addReminder(type, parseInt(days));
}

// Добавление напоминания
async function addReminder(type, frequencyDays) {
    try {
        const response = await fetch(`${API_URL}/plants/${currentPlantId}/reminders`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ reminder_type: type, frequency_days: frequencyDays })
        });
        
        if (response.ok) {
            showNotification('Напоминание добавлено!');
            showPlantDetail(currentPlantId);
        }
    } catch (error) {
        showNotification('Ошибка при добавлении напоминания');
    }
}

// Выполнить напоминание
window.completeReminder = async function(reminderId) {
    try {
        const response = await fetch(`${API_URL}/reminders/${reminderId}/complete`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            showNotification('Напоминание выполнено!');
            showPlantDetail(currentPlantId);
        }
    } catch (error) {
        showNotification('Ошибка');
    }
}

// Загрузка напоминаний
async function loadReminders() {
    try {
        const response = await fetch(`${API_URL}/reminders/upcoming`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.ok) {
            const reminders = await response.json();
            displayReminders(reminders);
        }
    } catch (error) {
        console.error('Failed to load reminders:', error);
    }
}

// Отображение напоминаний
function displayReminders(reminders) {
    const container = document.getElementById('reminders-list');
    
    if (reminders.length === 0) {
        container.innerHTML = '<p>Нет предстоящих напоминаний</p>';
        return;
    }
    
    container.innerHTML = reminders.map(rem => `
        <div class="reminder-card">
            <h3>${rem.plant_name} - ${rem.reminder_type}</h3>
            <div class="time">${new Date(rem.next_reminder).toLocaleString('ru-RU')}</div>
        </div>
    `).join('');
}

