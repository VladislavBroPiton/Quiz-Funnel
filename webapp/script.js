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
    submitBtn.textContent = '⏳ Отправка...';

    let width = 0;
    const interval = setInterval(() => {
        if (width >= 90) clearInterval(interval);
        else {
            width += 10;
            progressFill.style.width = width + '%';
        }
    }, 100);

    // Заново читаем значения полей, чтобы избежать проблем с областью видимости
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
        clearInterval(interval);
        progressFill.style.width = '100%';
        setTimeout(() => tg.close(), 1500);
    } catch (err) {
        console.error(err);
        clearInterval(interval);
        progressBar.style.display = 'none';
        errorDiv.textContent = 'Ошибка отправки. Попробуйте позже.';
        errorDiv.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.textContent = '✅ Узнать результат';
    }
});
