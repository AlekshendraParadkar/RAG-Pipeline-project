// frontend/app.js
(() => {
  const API_BASE = "http://127.0.0.1:8000"
    document.body.getAttribute('data-api-base')?.trim() ||
    window.location.origin;

  // Elements
  const tabLogin = document.getElementById('tab-login');
  const tabRegister = document.getElementById('tab-register');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  const authMsg = document.getElementById('auth-msg');
  const authCard = document.getElementById('auth-card');
  const chatCard = document.getElementById('chat-card');
  const messages = document.getElementById('messages');
  const askForm = document.getElementById('ask-form');
  const questionInput = document.getElementById('question');
  const whoami = document.getElementById('whoami');
  const logoutBtn = document.getElementById('logout-btn');

  // Token handling
  const TOKEN_KEY = 'access_token';
  const getToken = () => localStorage.getItem(TOKEN_KEY);
  const setToken = (t) => localStorage.setItem(TOKEN_KEY, t);
  const clearToken = () => localStorage.removeItem(TOKEN_KEY);

  // UI helpers
  function switchToLogin() {
    tabLogin.className = 'px-3 py-2 bg-blue-600 text-white rounded';
    tabRegister.className = 'px-3 py-2 bg-gray-200 text-gray-800 rounded';
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
    authMsg.className = 'text-sm text-red-600 mt-2';
    authMsg.textContent = '';
  }

  function switchToRegister() {
    tabRegister.className = 'px-3 py-2 bg-blue-600 text-white rounded';
    tabLogin.className = 'px-3 py-2 bg-gray-200 text-gray-800 rounded';
    registerForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    authMsg.className = 'text-sm text-red-600 mt-2';
    authMsg.textContent = '';
  }

  function showChat(username) {
    whoami.textContent = username ? `Signed in as ${username}` : '';
    authCard.classList.add('hidden');
    chatCard.classList.remove('hidden');
    messages.innerHTML = '';
    appendMsg('System', 'Logged in successfully.');
  }

  function showAuth(errorMsg = '') {
    chatCard.classList.add('hidden');
    authCard.classList.remove('hidden');
    if (errorMsg) {
      authMsg.className = 'text-sm text-red-600 mt-2';
      authMsg.textContent = errorMsg;
    }
  }

  function appendMsg(sender, text) {
    const div = document.createElement('div');
    div.className = 'mb-2';
    div.innerHTML = `<span class="font-medium">${sender}:</span> <span class="whitespace-pre-wrap">${text}</span>`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
  }

  // Network helpers
  async function postJSON(path, body, auth = false) {
    const headers = {'Content-Type': 'application/json'};
    if (auth) headers['Authorization'] = `Bearer ${getToken()}`;
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      if (res.status === 401 && auth) {
        clearToken();
        showAuth('Session expired. Please login again.');
      }
      throw new Error(data.detail || data.message || `Request failed (${res.status})`);
    }
    return data;
  }

  async function postForm(path, form) {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: form.toString(),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
    return data;
  }

  async function getJSON(path, auth = false) {
    const headers = {};
    if (auth) headers['Authorization'] = `Bearer ${getToken()}`;
    const res = await fetch(`${API_BASE}${path}`, { headers });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      if (res.status === 401 && auth) {
        clearToken();
        showAuth('Session expired. Please login again.');
      }
      throw new Error(data.detail || `Request failed (${res.status})`);
    }
    return data;
  }

  // Tab events
  tabLogin.onclick = switchToLogin;
  tabRegister.onclick = switchToRegister;

  // Register
  registerForm.onsubmit = async (e) => {
    e.preventDefault();
    authMsg.textContent = '';
    const username = document.getElementById('reg-username').value.trim();
    const password = document.getElementById('reg-password').value;
    if (username.length < 3 || password.length < 6) {
      authMsg.textContent = 'Invalid username or password length.';
      return;
    }
    try {
      await postJSON('/auth/register', { username, password });
      authMsg.className = 'text-sm text-green-700 mt-2';
      authMsg.textContent = 'Registered successfully, please login.';
      switchToLogin();
    } catch (err) {
      authMsg.className = 'text-sm text-red-600 mt-2';
      authMsg.textContent = err.message;
    }
  };

  // Login (OAuth2 form)
  loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  authMsg.textContent = '';
  const username = document.getElementById('login-username')?.value.trim() || '';
  const password = document.getElementById('login-password')?.value || '';

  try {
    const res = await fetch(`${API_BASE}/auth/login-json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');
    setToken(data.access_token);
    const me = await getJSON('/auth/me', true).catch(() => ({ username }));
    showChat(me.username || username);
  } catch (err) {
    authMsg.className = 'text-sm text-red-600 mt-2';
    authMsg.textContent = err.message;
  }
});

  // Ask protected
  askForm.onsubmit = async (e) => {
    e.preventDefault();
    const q = questionInput.value.trim();
    if (!q) return;
    appendMsg('You', q);
    questionInput.value = '';
    try {
      const data = await postJSON('/ask', { question: q }, true);
      appendMsg('Bot', data.answer || '(No answer)');
    } catch (err) {
      appendMsg('Error', err.message);
    }
  };

  // Logout
  logoutBtn.onclick = () => {
    clearToken();
    showAuth('Logged out.');
    switchToLogin();
  };

  // Boot: try token if present
  (async function init() {
    const token = getToken();
    if (!token) {
      showAuth();
      switchToLogin();
      return;
    }
    try {
      const me = await getJSON('/auth/me', true);
      showChat(me.username || '');
    } catch {
      clearToken();
      showAuth();
      switchToLogin();
    }
  })();
})();
