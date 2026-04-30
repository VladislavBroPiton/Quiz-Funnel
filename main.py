import asyncio, logging, os, json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web

from config import BOT_TOKEN, ADMIN_IDS, CALENDAR_ID
from database import Database
from google_sheets import append_quiz_result  # новый импорт для Google Sheets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()

EXPERT_IDS = list(map(int, os.getenv("EXPERT_IDS", "").split(","))) if os.getenv("EXPERT_IDS") else []

# ---------- Функция вычисления типа трейдера ----------
def determine_trader_type(experience, trading_style, goal, risk_level):
    if experience == 'beginner':
        if trading_style == 'scalping':
            return 'Активный новичок'
        else:
            return 'Осторожный старт'
    elif experience == 'intermediate':
        if risk_level == 'high':
            return 'Агрессивный трейдер'
        else:
            return 'Сбалансированный трейдер'
    else:  # experienced
        if goal == 'income':
            return 'Профессионал'
        else:
            return 'Инвестор'

# ---------- Команды ----------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await db.add_user(message.from_user.id, message.from_user.username)
    web_app_url = os.getenv("WEBAPP_URL", "https://your-app.onrender.com/webapp/")
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="📊 Пройти квиз трейдера", web_app=types.WebAppInfo(url=web_app_url))]],
        resize_keyboard=True
    )
    await message.answer("Привет! Пройди короткий квиз, чтобы узнать свой профиль трейдера и получить персональные рекомендации.", reply_markup=keyboard)

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not await db.is_admin(message.from_user.id) and message.from_user.id not in ADMIN_IDS:
        return
    results = await db.get_quiz_results(20)
    if not results:
        await message.answer("Нет результатов квизов.")
        return
    text = "*Последние результаты квиза:*\n"
    for r in results:
        text += (f"🆔 {r['id']} — @{r['username']} ({r['name']})\n"
                 f"📊 Тип: {r['result_type']}\n"
                 f"📞 {r['phone']}\n"
                 f"📅 {r['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
                 f"──────────────────\n")
    if len(text) > 4000:
        for part in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            await message.answer(part, parse_mode="Markdown")
    else:
        await message.answer(text, parse_mode="Markdown")

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if not await db.is_admin(message.from_user.id) and message.from_user.id not in ADMIN_IDS:
        return
    stats = await db.get_quiz_stats()
    text = (f"*📊 Статистика квиза*\n\n"
            f"Всего участников: {stats['total']}\n"
            f"Опытных трейдеров: {stats['experienced_percent']}%\n\n"
            f"*Распределение типов:*\n")
    for t in stats['by_type']:
        text += f"• {t['result_type']}: {t['count']}\n"
    await message.answer(text, parse_mode="Markdown")

# ---------- Обработка данных из Mini App ----------
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    user_id = message.from_user.id

    # Извлекаем ответы
    experience = data.get('experience')
    trading_style = data.get('trading_style')
    goal = data.get('goal')
    risk_level = data.get('risk_level')
    name = data.get('name')
    phone = data.get('phone')

    # Определяем тип
    result_type = determine_trader_type(experience, trading_style, goal, risk_level)
    
    # Сохраняем в БД
    quiz_id = await db.save_quiz_result(user_id, {
        'experience': experience,
        'trading_style': trading_style,
        'goal': goal,
        'risk_level': risk_level,
        'name': name,
        'phone': phone,
        'result_type': result_type
    })

    # Рекомендации (как в Mini App)
    recommendations = {
        'Активный новичок': 'Рекомендуем начать с демо-счета и изучить основы риск-менеджмента.',
        'Осторожный старт': 'Вам подойдут долгосрочные стратегии с низким риском.',
        'Агрессивный трейдер': 'Рассмотрите возможности маржинальной торговли и хеджирования.',
        'Сбалансированный трейдер': 'Продолжайте в том же духе! Возможно, стоит попробовать алгоритмическую торговлю.',
        'Профессионал': 'Отлично! Предлагаем вам доступ к нашей VIP-группе с сигналами.',
        'Инвестор': 'Вам подойдут портфельные инвестиции с горизонтом от 1 года.'
    }

    recommendation_text = recommendations.get(result_type, '')

    # --- НОВОЕ: запись в Google Sheets (если настроено) ---
    if os.getenv("GOOGLE_SHEETS_KEY"):
        try:
            append_quiz_result({
                "name": name,
                "phone": phone,
                "experience": experience,
                "trading_style": trading_style,
                "goal": goal,
                "risk_level": risk_level,
                "result_type": result_type,
                "recommendation": recommendation_text
            })
            logger.info(f"✅ Результат пользователя {name} записан в Google Sheets")
        except Exception as e:
            logger.error(f"❌ Ошибка записи в Google Sheets: {e}")

    # Ответ пользователю
    msg_text = (f"✅ Спасибо, {name}!\n\n"
                f"Ваш профиль трейдера: *{result_type}*\n\n"
                f"📌 *Рекомендация:* {recommendation_text}")

    await message.answer(msg_text, parse_mode="Markdown")

    # Уведомление админам/экспертам
    for admin_id in set(ADMIN_IDS + EXPERT_IDS):
        try:
            await bot.send_message(admin_id,
                f"🆕 *Новый квиз!*\n"
                f"Участник: {name} (@{message.from_user.username})\n"
                f"Тип: {result_type}\n"
                f"Телефон: {phone}",
                parse_mode="Markdown")
        except Exception as e:
            logger.warning(f"Не удалось уведомить {admin_id}: {e}")

# ---------- Эндпоинты API ----------
async def get_trader_types(request):
    return web.json_response([
        'Активный новичок', 'Осторожный старт', 'Агрессивный трейдер',
        'Сбалансированный трейдер', 'Профессионал', 'Инвестор'
    ])

# ---------- Webhook и статика ----------
async def handle_webhook(request):
    try:
        data = await request.json()
        update = types.Update(**data)
        await dp.feed_update(bot, update)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(status=200)

async def handle_health(request):
    return web.Response(text="OK")

async def webapp_index(request):
    return web.FileResponse('webapp/index.html')

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    DSN = os.getenv("DATABASE_URL")
    if not DSN:
        raise ValueError("DATABASE_URL missing")
    await db.create_pool(DSN)

    app = web.Application()
    app.router.add_get('/health', handle_health)
    app.router.add_post('/webhook', handle_webhook)
    app.router.add_get('/webapp/', webapp_index)
    app.router.add_static('/webapp/static', path='webapp/', show_index=False)
    app.router.add_get('/trader_types', get_trader_types)

    port = int(os.environ.get("PORT", 8000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"✅ Веб-сервер запущен на порту {port}")

    webhook_url = f"https://quiz-funnel-bot.onrender.com/webhook"
    await bot.set_webhook(url=webhook_url)
    logger.info(f"✅ Вебхук установлен: {webhook_url}")

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
