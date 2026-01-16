const API_URL = window.location.origin;
let token = localStorage.getItem('token');
let currentMemeId = null;

// Проверка авторизации при загрузке
window.onload = function() {
    if (token) {
        checkAuth();
    } else {
        showLogin();
    }
};

function showLogin() {
    document.getElementById('login-form').style.display = 'block';
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('user-info').style.display = 'none';
    document.getElementById('main-content').style.display = 'none';
}

function showRegister() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
    document.getElementById('user-info').style.display = 'none';
    document.getElementById('main-content').style.display = 'none';
}

async function register() {
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    try {
        const response = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });

        if (response.ok) {
            const data = await response.json();
            showMessage('Регистрация успешна! Теперь войдите.', 'success');
            showLogin();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка регистрации', 'error');
        }
    } catch (error) {
        showMessage('Ошибка подключения к серверу', 'error');
    }
}

async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
        const response = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            token = data.access_token;
            localStorage.setItem('token', token);
            await checkAuth();
        } else {
            showMessage('Неверное имя пользователя или пароль', 'error');
        }
    } catch (error) {
        showMessage('Ошибка подключения к серверу', 'error');
    }
}

async function checkAuth() {
    try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const user = await response.json();
            document.getElementById('username-display').textContent = user.username;
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('register-form').style.display = 'none';
            document.getElementById('user-info').style.display = 'block';
            document.getElementById('main-content').style.display = 'block';
            loadMemes();
        } else {
            logout();
        }
    } catch (error) {
        showMessage('Ошибка проверки авторизации', 'error');
    }
}

function logout() {
    token = null;
    localStorage.removeItem('token');
    showLogin();
    document.getElementById('main-content').style.display = 'none';
}

async function uploadImage() {
    const fileInput = document.getElementById('image-input');
    const file = fileInput.files[0];

    if (!file) {
        showMessage('Выберите файл', 'error', 'upload-status');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_URL}/api/memes/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            currentMemeId = data.id;
            showMessage('Изображение загружено успешно!', 'success', 'upload-status');
            document.getElementById('meme-section').style.display = 'block';
            loadMemes();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка загрузки', 'error', 'upload-status');
        }
    } catch (error) {
        showMessage('Ошибка подключения к серверу', 'error', 'upload-status');
    }
}

let textAlignments = { 0: 'center' }; // Храним выравнивание для каждого текста

function addTextInput() {
    const container = document.getElementById('text-inputs');
    const index = container.children.length;
    
    const groupDiv = document.createElement('div');
    groupDiv.className = 'text-input-group';
    groupDiv.setAttribute('data-index', index);
    
    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'text-input';
    input.placeholder = 'Введите текст для мема';
    input.setAttribute('data-index', index);
    
    const alignButtons = document.createElement('div');
    alignButtons.className = 'alignment-buttons';
    alignButtons.innerHTML = `
        <button class="align-btn" data-alignment="top" data-index="${index}" onclick="setAlignment(${index}, 'top')" title="Сверху">⬆️</button>
        <button class="align-btn active" data-alignment="center" data-index="${index}" onclick="setAlignment(${index}, 'center')" title="По центру">➖</button>
        <button class="align-btn" data-alignment="bottom" data-index="${index}" onclick="setAlignment(${index}, 'bottom')" title="Снизу">⬇️</button>
    `;
    
    groupDiv.appendChild(input);
    groupDiv.appendChild(alignButtons);
    container.appendChild(groupDiv);
    
    // Устанавливаем выравнивание по умолчанию
    textAlignments[index] = 'center';
}

function setAlignment(index, alignment) {
    textAlignments[index] = alignment;
    
    // Обновляем активную кнопку
    const group = document.querySelector(`.text-input-group[data-index="${index}"]`);
    const buttons = group.querySelectorAll('.align-btn');
    buttons.forEach(btn => {
        if (btn.getAttribute('data-alignment') === alignment) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

async function createMeme() {
    if (!currentMemeId) {
        showMessage('Сначала загрузите изображение', 'error', 'meme-status');
        return;
    }

    const textInputs = document.querySelectorAll('.text-input');
    const texts = [];
    
    textInputs.forEach(input => {
        const text = input.value.trim();
        if (text.length > 0) {
            const index = parseInt(input.getAttribute('data-index'));
            const alignment = textAlignments[index] || 'center';
            texts.push({
                text: text,
                alignment: alignment
            });
        }
    });

    if (texts.length === 0) {
        showMessage('Введите хотя бы один текст', 'error', 'meme-status');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/memes/create/${currentMemeId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ texts }),
        });

        if (response.ok) {
            const data = await response.json();
            showMessage('Мем создан успешно!', 'success', 'meme-status');
            // Показываем превью созданного мема
            showMemePreview(currentMemeId);
            loadMemes();
        } else {
            const error = await response.json();
            showMessage(error.detail || 'Ошибка создания мема', 'error', 'meme-status');
        }
    } catch (error) {
        showMessage('Ошибка подключения к серверу', 'error', 'meme-status');
    }
}

async function loadMemes() {
    try {
        const response = await fetch(`${API_URL}/api/memes/list`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const memes = await response.json();
            displayMemes(memes);
        }
    } catch (error) {
        console.error('Ошибка загрузки мемов:', error);
    }
}

async function loadMemeImage(memeId) {
    try {
        const response = await fetch(`${API_URL}/api/memes/image/${memeId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const blob = await response.blob();
            return URL.createObjectURL(blob);
        }
        return null;
    } catch (error) {
        console.error('Ошибка загрузки изображения:', error);
        return null;
    }
}

async function displayMemes(memes) {
    const container = document.getElementById('meme-list');
    container.innerHTML = '';

    if (memes.length === 0) {
        container.innerHTML = '<p>У вас пока нет мемов</p>';
        return;
    }

    for (const meme of memes) {
        const memeDiv = document.createElement('div');
        memeDiv.className = 'meme-item';
        
        // Загружаем изображение с авторизацией
        const imageUrl = await loadMemeImage(meme.id);
        
        memeDiv.innerHTML = `
            <div class="meme-image-container">
                ${imageUrl 
                    ? `<img src="${imageUrl}" alt="${meme.filename}" class="meme-image">`
                    : `<div class="meme-placeholder">Изображение не найдено</div>`
                }
            </div>
            <div class="meme-info">
                <p><strong>${meme.filename}</strong></p>
                <p>Создан: ${new Date(meme.created_at).toLocaleString('ru-RU')}</p>
                <button onclick="downloadMeme(${meme.id})">Скачать мем</button>
            </div>
        `;
        container.appendChild(memeDiv);
    }
}

async function downloadMeme(memeId) {
    try {
        const response = await fetch(`${API_URL}/api/memes/download/${memeId}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `meme_${memeId}.png`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            showMessage('Ошибка скачивания мема', 'error');
        }
    } catch (error) {
        showMessage('Ошибка подключения к серверу', 'error');
    }
}

async function showMemePreview(memeId) {
    // Создаем превью созданного мема
    const memeSection = document.getElementById('meme-section');
    
    // Удаляем старое превью, если есть
    const oldPreview = document.getElementById('meme-preview');
    if (oldPreview) {
        oldPreview.remove();
    }
    
    const previewDiv = document.createElement('div');
    previewDiv.id = 'meme-preview';
    previewDiv.className = 'meme-preview';
    previewDiv.innerHTML = `
        <h3>Ваш мем:</h3>
        <div class="preview-loading">Загрузка...</div>
    `;
    memeSection.appendChild(previewDiv);
    
    // Загружаем изображение
    const imageUrl = await loadMemeImage(memeId);
    if (imageUrl) {
        const loadingDiv = previewDiv.querySelector('.preview-loading');
        loadingDiv.outerHTML = `<img src="${imageUrl}" alt="Превью мема" class="preview-image">`;
    } else {
        const loadingDiv = previewDiv.querySelector('.preview-loading');
        loadingDiv.textContent = 'Ошибка загрузки изображения';
    }
}

function showMessage(message, type, elementId = 'upload-status') {
    const statusDiv = document.getElementById(elementId);
    statusDiv.textContent = message;
    statusDiv.className = type;
    statusDiv.style.display = 'block';

    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}

