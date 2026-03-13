import json
import os
from datetime import datetime

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.apilayer.com/exchangerates_data/convert"
# Путь к настройкам лучше вынести в константу или определять относительно корня проекта
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), '..', 'user_settings.json')


def get_greeting(dt: datetime) -> str:
    """Возвращает приветствие в зависимости от времени суток.

    Args:
        dt: Объект datetime для определения часа.

    Returns:
        Строка с приветствием (например, 'Доброе утро').
    """
    hour = dt.hour
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_currency_rates(currencies: list) -> list:
    """Получает курсы валют к рублю через API.

    Args:
        currencies: Список кодов валют (например, ['USD', 'EUR']).

    Returns:
        Список словарей с кодом валюты и ее курсом.
    """
    rates = []
    if not API_KEY:
        print("Ошибка: API_KEY не найден в переменных окружения.")
        return rates

    for curr in currencies:
        params = {"to": "RUB", "from": curr, "amount": 1}
        try:
            response = requests.get(
                BASE_URL,
                params=params,
                headers={"apikey": API_KEY},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                rates.append({
                    "currency": curr,
                    "rate": round(data.get('result', 0), 2)
                })
        except Exception as e:
            print(f"Ошибка при получении курса {curr}: {e}")
    return rates


def get_stock_prices(stocks: list) -> list:
    """Получает текущие цены акций через библиотеку yfinance.

    Args:
        stocks: Список тикеров акций (например, ['AAPL', 'TSLA']).

    Returns:
        Список словарей с тикером и ценой закрытия за последний торговый день.
    """
    stock_prices = []
    for stock in stocks:
        try:
            ticker = yf.Ticker(stock)
            history = ticker.history(period="1d")

            if not history.empty:
                current_price = history['Close'].iloc[-1]
                stock_prices.append({
                    "stock": stock,
                    "price": round(float(current_price), 2)
                })
            else:
                stock_prices.append({"stock": stock, "price": 0.0})
        except Exception as e:
            print(f"Ошибка при получении цены акции {stock}: {e}")
            stock_prices.append({"stock": stock, "price": 0.0})
    return stock_prices


def main_dashboard(date_str: str, df: pd.DataFrame) -> str:
    """Формирует итоговый JSON для главной страницы дашборда."""

    # 1. ПРЕОБРАЗОВАНИЕ даты
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)

    # 2. Парсинг входной даты и определение границ месяца
    target_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    start_month = target_date.replace(day=1, hour=0, minute=0, second=0)

    # 3. Фильтрация данных за месяц (от 1-го числа до target_date)
    mask = (df['Дата операции'] >= start_month) & (df['Дата операции'] <= target_date)
    filtered_df = df.loc[mask].copy()

    # 4. Информация по картам (расходы)
    cards = []
    expenses = filtered_df[filtered_df['Сумма операции'] < 0]

    # Группируем по картам, считаем общую сумму и кэшбэк
    for card_number, group in expenses.groupby('Номер карты', dropna=True):
        total_spent = abs(group['Сумма операции'].sum())
        cards.append({
            "last_digits": str(card_number).replace('*', ''),
            "total_spent": round(total_spent, 2),
            "cashback": round(total_spent / 100, 2)
        })

    # 5. Топ-5 транзакций по абсолютной сумме
    top_5_df = filtered_df[filtered_df['Сумма операции'] < 0] \
        .assign(abs_sum=filtered_df['Сумма операции'].abs()) \
        .sort_values(by='abs_sum', ascending=False) \
        .head(5)

    top_transactions = [{
        "date": row['Дата операции'].strftime('%d.%m.%Y'),
        "amount": row['Сумма операции'],
        "category": row['Категория'],
        "description": row['Описание']
    } for _, row in top_5_df.iterrows()]

    # Безопасная загрузка настроек
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Если файла нет ИЛИ он "битый" (ошибка декодирования), создаем пустой словарь
        settings = {}
        print(f"Предупреждение: файл настроек не загружен ({e}). Использованы значения по умолчанию.")

    # 6. Сборка итогового результата
    result = {
        "greeting": get_greeting(target_date),
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": get_currency_rates(settings.get("user_currencies", [])),
        "stock_prices": get_stock_prices(settings.get("user_stocks", []))
    }

    return json.dumps(result, ensure_ascii=False, indent=4)
