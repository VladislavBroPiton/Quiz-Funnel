import json
import os
import logging
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)

SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID", "ваш_дефолтный_sheet_id")
WORKSHEET_NAME = "Quiz"

# Словари перевода значений на русский
EXPERIENCE_MAP = {
    "beginner": "Новичок",
    "intermediate": "Продвинутый",
    "experienced": "Профессионал"
}

TRADING_STYLE_MAP = {
    "scalping": "Скальпинг",
    "day_trading": "Дейтрейдинг",
    "swing": "Свинг",
    "long_term": "Долгосрочные инвестиции"
}

GOAL_MAP = {
    "income": "Стабильный доход",
    "growth": "Рост капитала",
    "speculation": "Спекуляция"
}

RISK_LEVEL_MAP = {
    "low": "Консервативный (до 1%)",
    "medium": "Умеренный (1-3%)",
    "high": "Агрессивный (более 3%)"
}

def _get_google_client():
    creds_json = os.getenv("GOOGLE_SHEETS_KEY")
    if not creds_json:
        raise ValueError("❌ Переменная окружения GOOGLE_SHEETS_KEY не задана.")
    
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        creds_dict = json.loads(creds_json)
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(credentials)
        logger.info("✅ Google Sheets клиент успешно авторизован")
        return client
    except Exception as e:
        logger.error(f"❌ Ошибка авторизации Google Sheets: {e}")
        raise

def append_quiz_result(data: dict):
    try:
        client = _get_google_client()
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        
        # Проверяем, существует ли нужный лист, и создаём при необходимости
        try:
            sheet = spreadsheet.worksheet(WORKSHEET_NAME)
        except gspread.WorksheetNotFound:
            logger.info(f"Лист '{WORKSHEET_NAME}' не найден, создаю новый...")
            sheet = spreadsheet.add_worksheet(WORKSHEET_NAME, rows="1000", cols="20")
            # Добавляем заголовки
            headers = ["Дата", "Имя", "Телефон", "Опыт", "Стиль", "Цель", "Риск", "Тип трейдера", "Рекомендация"]
            sheet.append_row(headers, value_input_option="USER_ENTERED")

        # Переводим значения на русский
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("name", ""),
            data.get("phone", ""),
            EXPERIENCE_MAP.get(data.get("experience", ""), data.get("experience", "")),
            TRADING_STYLE_MAP.get(data.get("trading_style", ""), data.get("trading_style", "")),
            GOAL_MAP.get(data.get("goal", ""), data.get("goal", "")),
            RISK_LEVEL_MAP.get(data.get("risk_level", ""), data.get("risk_level", "")),
            data.get("result_type", ""),
            data.get("recommendation", "")
        ]
        sheet.append_row(row, value_input_option="USER_ENTERED")
        logger.info(f"✅ Данные квиза добавлены в Google Sheets: {data.get('name')}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка записи в Google Sheets: {e}")
        return False
