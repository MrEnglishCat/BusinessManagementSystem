import { isLoggedIn, handleLogin, logout } from './auth.js';
import { renderRegister } from './pages/register.js';
import { renderDashboard } from './pages/dashboard.js';
import { renderUsers } from './pages/users.js';
import { renderTeams } from './pages/teams.js';
import { renderTasks } from './pages/tasks.js';
import { renderMeetings } from './pages/meetings.js';
import { renderEvaluations } from './pages/evaluations.js';

const app = document.getElementById('app');
const navbar = document.getElementById('navbar');

const routes = {
    '/login': handleLogin,
    '/register': renderRegister,
    '/': renderDashboard,
    '/dashboard': renderDashboard,
    '/users': renderUsers,
    '/teams': renderTeams,
    '/tasks': renderTasks,
    '/meetings': renderMeetings,
    '/evaluations': renderEvaluations,
};
function updateActiveLink() {
    const hash = window.location.hash.slice(1) || '/';
    document.querySelectorAll('nav a').forEach(link => {
        const linkHash = link.getAttribute('href').slice(1);
        link.classList.toggle('active', linkHash === hash);
    });
}

function router() {
    const hash = window.location.hash.slice(1) || '/login';
    
    if (!isLoggedIn() && hash !== '/login' && hash !== '/register') {
        window.location.hash = '#/login';
        return;
    }
    if (isLoggedIn() && (hash === '/login' || hash === '/register')) {
        window.location.hash = '#/';
        return;
    }

    navbar.classList.toggle('hidden', hash === '/login' || hash === '/register');
    app.innerHTML = '';
    
    const handler = routes[hash] || (() => { app.innerHTML = '<h2>404 Страница не найдена</h2><a href="#/">На главную</a>'; });
    handler(app);
    updateActiveLink();
}

window.addEventListener('hashchange', router);
document.getElementById('logout-btn').addEventListener('click', logout);

// Инициализация
router();