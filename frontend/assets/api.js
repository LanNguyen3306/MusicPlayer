
const API_URL = "http://127.0.0.1:8000";

function getToken() {
    return localStorage.getItem("access_token");
}

function setToken(token) {
    localStorage.setItem("access_token", token);
}

function checkAuth() {
    if (!getToken()) {
        window.location.href = "login.html";
    }
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
}

async function fetchAPI(endpoint, options = {}) {
    const headers = options.headers || {};
    const token = getToken();
    
    if (token && !headers['Authorization']) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = { ...options, headers };
    const res = await fetch(`${API_URL}${endpoint}`, config);
    
    if (res.status === 401) {
        logout();
    }
    return res;
}

function playSong(id, title, artist) {
    const playerContainer = document.getElementById('player-container');
    const audio = document.getElementById('audio-player');
    const nowPlaying = document.getElementById('now-playing');
    
    if (playerContainer) playerContainer.classList.remove('d-none');
    if (nowPlaying) nowPlaying.innerText = `Đang phát: ${title} - ${artist}`;
    if (audio) {
        audio.src = `${API_URL}/songs/${id}/play`;
        audio.play();
    }
}

async function toggleFavorite(id) {
    const res = await fetchAPI(`/songs/${id}/favorite`, { method: 'POST' });
    if (res.ok) {
        const data = await res.json();
        alert(data.message);
        if (window.location.pathname.includes('favorites.html')) {
            // Tải lại trang favorites nếu đang ở đó
            if (typeof loadFavorites === 'function') loadFavorites();
        }
    } else {
        alert("Có lỗi xảy ra.");
    }
}
