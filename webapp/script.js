const tg = window.Telegram.WebApp;
tg.ready();

const form = document.getElementById('quizForm');
const submitBtn = document.getElementById('submitBtn');
const errorDiv = document.getElementById('formError');
const progressBar = document.getElementById('progressBar');
const progressFill = progressBar.querySelector('.progress-fill');
const closeResultBtn = document.getElementById('closeResultBtn');
const progressSteps = document.querySelectorAll('.progress-step');

function updateProgressSteps(step) {
    progressSteps.forEach((dot, index) => {
        dot.classList.remove('active', 'completed');
        if (index + 1 === step) dot.classList.add('active');
        else if (index + 1 < step) dot.classList.add('completed');
    });
}

let currentStep = 1;
const steps = document.querySelectorAll('.step');

function showStep(step) {
    steps.forEach((s, idx) => s.classList.toggle('active', idx === step - 1));
    currentStep = step;
    updateProgressSteps(step);
    updateNextButton();
}

function updateNextButton() {
    const activeStep = document.querySelector('.step.active');
    if (!activeStep) return;
    const nextBtn = activeStep.querySelector('.next-btn');
    if (!nextBtn) return;
    const grid = activeStep.querySelector('.options-grid');
    if (grid) {
        const name = grid.getAttribute('data-name');
        const selected = grid.querySelector('.option-card.selected');
        nextBtn.disabled = !selected;
        if (selected && name) {
            form[name].value = selected.getAttribute('data-value');
        }
    }
}

// Обработка выбора карточек
document.querySelectorAll('.options-grid').forEach(grid => {
    grid.addEventListener('click', (e) => {
        const card = e.target.closest('.option-card');
        if (!card) return;
        grid.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        const name = grid.getAttribute('data-name');
        if (name) {
            form[name].value = card.getAttribute('data-value');
        }
        updateNextButton();
        saveFormData();
    });
});

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

// Подсказки
const tooltipPopup = document.getElementById('tooltipPopup');
document.querySelectorAll('.tooltip-trigger').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        const text = trigger.getAttribute('data-tooltip');
        const rect = trigger.getBoundingClientRect();
        tooltipPopup.textContent = text;
        tooltipPopup.style.left = (rect.left + rect.width/2 - 80) + 'px';
        tooltipPopup.style.top = (rect.bottom + 10) + 'px';
        tooltipPopup.classList.add('visible');
        setTimeout(() => tooltipPopup.classList.remove('visible'), 2000);
    });
});
document.addEventListener('click', () => tooltipPopup.classList.remove('visible'));

function saveFormData() {
    const data = {};
    document.querySelectorAll('.options-grid').forEach(grid => {
        const name = grid.getAttribute('data-name');
        const selected = grid.querySelector('.option-card.selected');
        if (selected) {
            data[name] = selected.getAttribute('data-value');
            if (form[name]) form[name].value = selected.getAttribute('data-value');
        }
    });
    data.name = form.name.value;
    data.phone = form.phone.value;
    localStorage.setItem('quiz_form', JSON.stringify(data));
}

function loadSavedData() {
    const saved = localStorage.getItem('quiz_form');
    if (saved) {
        const data = JSON.parse(saved);
        document.querySelectorAll('.options-grid').forEach(grid => {
            const name = grid.getAttribute('data-name');
            if (data[name]) {
                const card = grid.querySelector(`.option-card[data-value="${data[name]}"]`);
                if (card) {
                    grid.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
                    card.classList.add('selected');
                }
            }
        });
        form.name.value = data.name || '';
        form.phone.value = data.phone || '';
        updateNextButton();
    }
}
loadSavedData();
form.addEventListener('input', saveFormData);

function validateForm() {
    const name = form.name.value.trim();
    const phone = form.phone.value.trim();
    if (!name) return "Введите имя";
    if (!phone) return "Введите телефон";
    const phoneRegex = /^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$/;
    if (!phoneRegex.test(phone)) return "Некорректный номер телефона";
    return null;
}

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
            showResult();
        } else {
            progressFill.style.width = width + '%';
        }
    }, 80);

    function getType() {
        const exp = form.experience.value;
        const style = form.trading_style.value;
        const goal = form.goal.value;
        const risk = form.risk_level.value;
        if (exp === 'beginner') return style === 'scalping' ? 'Активный новичок' : 'Осторожный старт';
        else if (exp === 'intermediate') return risk === 'high' ? 'Агрессивный трейдер' : 'Сбалансированный трейдер';
        else return goal === 'income' ? 'Профессионал' : 'Инвестор';
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

    let pendingFormData = null;

    function showResult() {
        const type = getType();
        const resultCard = document.getElementById('resultCard');
        resultCard.setAttribute('data-type', type);
        document.getElementById('resultType').textContent = type;
        document.getElementById('resultRecommendation').textContent = recommendations[type] || '';
        document.getElementById('resultIcon').innerHTML = `<span class="icon-animated">${icons[type]}</span>`;

        form.style.display = 'none';
        resultCard.style.display = 'block';
        progressBar.style.display = 'none';
        document.getElementById('progressSteps').style.display = 'none';

        const name = form.name.value.trim();
        const phone = form.phone.value.trim();
        pendingFormData = {
            experience: form.experience.value,
            trading_style: form.trading_style.value,
            goal: form.goal.value,
            risk_level: form.risk_level.value,
            name: name,
            phone: phone
        };
    }

    if (closeResultBtn) {
        closeResultBtn.addEventListener('click', () => {
            if (pendingFormData) {
                try { tg.sendData(JSON.stringify(pendingFormData)); } catch (err) { console.error(err); }
            }
            tg.close();
        });
    }
});
