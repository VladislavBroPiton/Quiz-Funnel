# 📊 Quiz Trader Bot

**Telegram Mini App для определения профиля трейдера с персонализированными рекомендациями.**

[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/QuizFunnelBot)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-black?logo=github)](https://github.com/VladislavBroPiton/Quiz-Funnel)
[![Render Deploy](https://img.shields.io/badge/Deployed%20on-Render-46e3b7?logo=render)](https://render.com)

---

## 📸 Обзор

<details>
<summary>📱 Mini App — шаги квиза</summary>

![Quiz Steps](https://placehold.co/600x400/2AABEE/white?text=Quiz+Steps)

- 5 шагов: опыт → стиль → цель → риск → контакты
- Анимированные карточки ответов с иконками
- Индикатор прогресса и подсказки к вопросам
- Тёмная и светлая темы с сохранением выбора

</details>

<details>
<summary>🏆 Карточка результата</summary>

![Result Card](https://placehold.co/600x400/10B981/white?text=Result+Card)

- WOW-анимация появления
- Анимированная иконка, уникальная для каждого типа трейдера
- Тематический фон под каждый тип
- Три персональных совета с эмодзи
- Кнопка «Понятно, закрыть»

</details>

<details>
<summary>📊 Google Sheets — автоматическая запись</summary>

![Google Sheets](https://placehold.co/600x400/F59E0B/white?text=Google+Sheets)

- Результаты квиза автоматически попадают в таблицу
- Значения переводятся на русский язык
- Заголовки создаются автоматически при первом запуске

</details>

---

## 🚀 Ключевые возможности

- **📱 Telegram Mini App** — современный интерфейс с анимациями, темами и подсказками
- **🤖 Telegram-бот** (aiogram 3.x) — обработка команд, вычисление типа трейдера, выдача рекомендаций
- **📊 Интеграция с Google Sheets** — автоматическая запись результатов в таблицу
- **🗄️ PostgreSQL** (Neon) — хранение пользователей и истории квизов
- **👑 Админ-панель** — просмотр последних результатов и статистики прямо в боте
- **📈 Уведомления** — админы и эксперты получают сообщение о каждом новом квизе
- **🌐 Деплой на Render** — с вебхуками, healthcheck и автосбросом старых обновлений
- **🎨 Тёмная/светлая тема** — переключается одной кнопкой, сохраняется в localStorage
- **💾 Автосохранение** — данные формы сохраняются в localStorage, чтобы не потерять прогресс

---

## 🛠️ Технологический стек

| Компонент | Технология |
|-----------|------------|
| Бэкенд | Python 3.12, aiogram 3.x, aiohttp |
| База данных | PostgreSQL (asyncpg, Neon) |
| Mini App | HTML, CSS, JavaScript, Telegram Web App API |
| Google Sheets | gspread, oauth2client |
| Деплой | Render, CronJob |
| Шрифты | Inter, Google Fonts |


