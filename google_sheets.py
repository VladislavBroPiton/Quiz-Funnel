import json
import os
import logging
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)

# ID вашей Google таблицы
SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID", "ваш_дефолтный_sheet_id")
# Название листа, куда будем записывать данные (по умолчанию sheet1)
WORKSHEET_NAME = "Sheet1"

def _get_google_client():
    """
    Создаёт и возвращает авторизованный клиент gspread.
    """
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
    """
    Добавляет одну строку с результатами квиза в Google Sheets.
    Ожидает словарь data с ключами:
    name, phone, experience, trading_style, goal, risk_level, result_type, recommendation
    """
    try:
        client = _get_google_client()
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)
        
        # Формируем строку для добавления (порядок должен совпадать с заголовками)
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("name", ""),
            data.get("phone", ""),
            data.get("experience", ""),
            data.get("trading_style", ""),
            data.get("goal", ""),
            data.get("risk_level", ""),
            data.get("result_type", ""),
            data.get("recommendation", "")
        ]
        
        sheet.append_row(row, value_input_option="USER_ENTERED")
        logger.info(f"✅ Данные квиза добавлены в Google Sheets: {data.get('name')}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка записи в Google Sheets: {e}")
        return False
