import json
import os
import logging
from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)

SPREADSHEET_ID = os.getenv("GOOGLE_SHEET_ID", "ваш_дефолтный_sheet_id")
WORKSHEET_NAME = "Sheet1"   # можешь поменять на любое удобное имя

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
            # Добавляем заголовки (опционально, если лист был только что создан)
            headers = ["Дата", "Имя", "Телефон", "Опыт", "Стиль", "Цель", "Риск", "Тип трейдера", "Рекомендация"]
            sheet.append_row(headers, value_input_option="USER_ENTERED")

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
