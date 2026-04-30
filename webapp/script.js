const tg = window.Telegram.WebApp;
tg.ready();

const form = document.getElementById('quizForm');
const submitBtn = document.getElementById('submitBtn');
const errorDiv = document.getElementById('formError');
const progressBar = document.getElementById('progressBar');
const progressFill = progressBar.querySelector('.progress-fill');

// Шаги
let currentStep = 1;
const steps = document.querySelectorAll('.step');

function showStep(step) {
    steps.forEach((s, idx) => {
        s.classList.toggle('active', idx === step - 1);
    });
    currentStep = step;
}

document.querySelectorAll('.next-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        if (currentStep < steps.length) showStep(currentStep + 1);
    });
});
document.querySelectorAll('.prev-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        if (currentStep > 1) showStep(currentStep - 1);
    });
});
showStep(1);

// Сохранение в localStorage
function saveFormData() {
    const data = {
        experience: form.experience.value,
        trading_style: form.trading_style.value,
        goal: form.goal.value,
        risk_level: form.risk_level.value,
        name: form.name.value,
        phone: form.phone.value
    };
    localStorage.setItem('quiz_form', JSON.stringify(data));
}

function loadSavedData() {
    const saved = localStorage.getItem('quiz_form');
    if (saved) {
        const data = JSON.parse(saved);
        form.experience.value = data.experience || 'beginner';
        form.trading_style.value = data.trading_style || 'day_trading';
        form.goal.value = data.goal || 'income';
        form.risk_level.value = data.risk_level || 'low';
        form.name.value = data.name || '';
        form.phone.value = data.phone || '';
    }
}
loadSavedData();
form.addEventListener('input', saveFormData);

// Валидация
function validateForm() {
    const name = form.name.value.trim();
    const phone = form.phone.value.trim();
    if (!name) return "Введите имя";
    if (!phone) return "Введите телефон";
    const phoneRegex = /^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$/;
    if (!phoneRegex.test(phone)) return "Некорректный номер телефона";
    return null;
}

// Отправка
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const err = validateForm();
    if (err) {
        errorDiv.textContent = err;
        errorDiv.style.display = 'block';
        return;
    }
    errorDiv.style.display = 'none';
    progressBar.style.display = 'block';
    progressFill.style.width = '0%';
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Анализируем...';

    let width = 0;
    const interval = setInterval(() => {
        width += 7;
        if (width >= 100) {
            width = 100;
            clearInterval(interval);
            progressFill.style.width = '100%';
            // Показываем результат с wow-эффектом
            showResult();
        } else {
            progressFill.style.width = width + '%';
        }
    }, 80);

    // Определяем тип трейдера локально (та же логика, что в боте)
    function getType() {
        const exp = form.experience.value;
        const style = form.trading_style.value;
        const goal = form.goal.value;
        const risk = form.risk_level.value;

        if (exp === 'beginner') {
            return style === 'scalping' ? 'Активный новичок' : 'Осторожный старт';
        } else if (exp === 'intermediate') {
            return risk === 'high' ? 'Агрессивный трейдер' : 'Сбалансированный трейдер';
        } else {
            return goal === 'income' ? 'Профессионал' : 'Инвестор';
        }
    }

    const recommendations = {
        'Активный новичок': 'Рекомендуем начать с демо-счета и изучить основы риск-менеджмента.',
        'Осторожный старт': 'Вам подойдут долгосрочные стратегии с низким риском.',
        'Агрессивный трейдер': 'Рассмотрите возможности маржинальной торговли и хеджирования.',
        'Сбалансированный трейдер': 'Продолжайте в том же духе! Возможно, стоит попробовать алгоритмическую торговлю.',
        'Профессионал': 'Отлично! Предлагаем вам доступ к нашей VIP-группе с сигналами.',
        'Инвестор': 'Вам подойдут портфельные инвестиции с горизонтом от 1 года.'
    };

    const icons = {
        'Активный новичок': '🚀',
        'Осторожный старт': '🐢',
        'Агрессивный трейдер': '🔥',
        'Сбалансированный трейдер': '⚖️',
        'Профессионал': '🏆',
        'Инвестор': '💼'
    };

    function showResult() {
        const type = getType();
        document.getElementById('resultType').textContent = type;
        document.getElementById('resultRecommendation').textContent = recommendations[type] || '';
        document.getElementById('resultIcon').textContent = icons[type] || '📊';

        // Скрываем форму и показываем карточку
        form.style.display = 'none';
        document.getElementById('resultCard').style.display = 'block';
        progressBar.style.display = 'none';

        // Отправляем данные на бэкенд в фоне
        const name = form.name.value.trim();
        const phone = form.phone.value.trim();
        const formData = {
            experience: form.experience.value,
            trading_style: form.trading_style.value,
            goal: form.goal.value,
            risk_level: form.risk_level.value,
            name: name,
            phone: phone
        };
        try {
            tg.sendData(JSON.stringify(formData));
        } catch (err) {
            console.error(err);
        }

        // Закрываем Mini App через 10 секунд, чтобы пользователь успел сделать скриншот
        setTimeout(() => {
            tg.close();
        }, 15000);
    }
});
