// Данные товаров
const products = [
  { id: 1, name: 'Футбольный мяч Adidas', price: 2500, category: 'ball' },
  { id: 2, name: 'Баскетбольный мяч Spalding', price: 2200, category: 'ball' },
  { id: 3, name: 'Беговые кроссовки Nike', price: 8900, category: 'shoes' },
  { id: 4, name: 'Тренировочные кроссовки Puma', price: 6500, category: 'shoes' },
  { id: 5, name: 'Теннисная ракетка Wilson', price: 6200, category: 'equipment' },
  { id: 6, name: 'Йога-коврик Reebok', price: 1800, category: 'equipment' },
  { id: 7, name: 'Спортивная сумка Puma', price: 3400, category: 'accessories' },
  { id: 8, name: 'Перчатки для бокса Everlast', price: 4100, category: 'accessories' }
];

// DOM элементы
const body = document.body;
const homeSection = document.getElementById('home');
const catalogSection = document.getElementById('catalog-section');
const catalogEl = document.getElementById('catalog');
const cartIcon = document.getElementById('cart-icon');
const cartModal = document.getElementById('cart-modal');
const cartItemsEl = document.getElementById('cart-items');
const cartTotalEl = document.getElementById('cart-total');
const cartCountEl = document.getElementById('cart-count');
const checkoutBtn = document.getElementById('checkout-btn');
const closeCartBtn = document.getElementById('close-cart');
const themeToggleBtn = document.getElementById('theme-toggle');
const goToCatalogBtn = document.getElementById('go-to-catalog');
const categoryButtons = document.querySelectorAll('.category-btn');

// Инициализация
let cart = JSON.parse(localStorage.getItem('cart')) || [];
let currentCategory = 'all';
let isDarkTheme = localStorage.getItem('theme') === 'dark';

// Применение темы
function applyTheme() {
  if (isDarkTheme) {
    body.setAttribute('data-theme', 'dark');
    themeToggleBtn.textContent = '☀️';
  } else {
    body.removeAttribute('data-theme');
    themeToggleBtn.textContent = '🌙';
  }
  localStorage.setItem('theme', isDarkTheme ? 'dark' : 'light');
}

// Переключение темы
themeToggleBtn.addEventListener('click', () => {
  isDarkTheme = !isDarkTheme;
  applyTheme();
});

// Переключение на каталог
goToCatalogBtn.addEventListener('click', () => {
  homeSection.classList.add('hidden');
  catalogSection.classList.remove('hidden');
  document.querySelector('.categories').classList.remove('hidden');
  cartIcon.classList.remove('hidden');
  renderCatalog(currentCategory);
});

// Отображение товаров
function renderCatalog(category = 'all') {
  const filtered = category === 'all'
    ? products
    : products.filter(p => p.category === category);

  catalogEl.innerHTML = filtered.length
    ? filtered.map(product => `
        <div class="product-card">
          <h3>${product.name}</h3>
          <p class="price">${product.price} ₽</p>
          <button onclick="addToCart(${product.id})">В корзину</button>
        </div>
      `).join('')
    : '<p>Нет товаров в этой категории.</p>';
}

// Корзина
function addToCart(productId) {
  const product = products.find(p => p.id === productId);
  if (!product) return;

  const existing = cart.find(item => item.id === productId);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({ ...product, quantity: 1 });
  }

  saveCart();
  updateCartUI();
}

function removeFromCart(productId) {
  cart = cart.filter(item => item.id !== productId);
  saveCart();
  updateCartUI();
}

function saveCart() {
  localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCartUI() {
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  cartCountEl.textContent = totalItems;

  // Обновление кнопки оформления
  checkoutBtn.disabled = cart.length === 0;

  if (cart.length === 0) {
    cartItemsEl.innerHTML = '<p>Корзина пуста</p>';
    cartTotalEl.textContent = 'Итого: 0 ₽';
  } else {
    cartItemsEl.innerHTML = cart.map(item => `
      <div class="cart-item">
        <div>
          <strong>${item.name}</strong> × ${item.quantity}
        </div>
        <div style="display:flex;align-items:center;gap:0.5rem;">
          ${item.price * item.quantity} ₽
          <button onclick="removeFromCart(${item.id})">Удалить</button>
        </div>
      </div>
    `).join('');

    const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
    cartTotalEl.textContent = `Итого: ${total} ₽`;
  }
}

// Инициализация
document.addEventListener('DOMContentLoaded', () => {
  applyTheme();
  updateCartUI();

  // Категории
  categoryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      categoryButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentCategory = btn.dataset.category;
      renderCatalog(currentCategory);
    });
  });

  // Корзина
  cartIcon.addEventListener('click', () => {
    cartModal.classList.remove('hidden');
  });

  closeCartBtn.addEventListener('click', () => {
    cartModal.classList.add('hidden');
  });

  checkoutBtn.addEventListener('click', () => {
    if (cart.length === 0) return; // Защита (на всякий)
    alert('Заказ оформлен! Спасибо за покупку!');
    cart = [];
    saveCart();
    updateCartUI();
    cartModal.classList.add('hidden');
  });
});