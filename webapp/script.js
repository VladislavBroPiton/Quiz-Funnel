// Шаги от 1 до 5
let currentStep = 1;
const steps = document.querySelectorAll('.step');

// ... логика переключения шагов (как в BeautyBook)

// При отправке
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    // простая валидация
    const formData = {
        experience: form.experience.value,
        trading_style: form.trading_style.value,
        goal: form.goal.value,
        risk_level: form.risk_level.value,
        name: form.name.value.trim(),
        phone: form.phone.value.trim()
    };
    tg.sendData(JSON.stringify(formData));
    // ... показать прогресс-бар, закрыть после ответа
});
