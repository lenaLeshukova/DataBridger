import json
from datetime import datetime
from unittest.mock import patch, MagicMock, mock_open

import pandas as pd
import pytest

from src.views import get_greeting, get_currency_rates, get_stock_prices, main_dashboard


# 1. Тесты для функции get_greeting
@pytest.mark.parametrize("hour, expected", [
    (7, "Доброе утро"),
    (13, "Добрый день"),
    (19, "Добрый вечер"),
    (2, "Доброй ночи"),
])
def test_get_greeting(hour, expected):
    dt = datetime(2023, 1, 1, hour)
    assert get_greeting(dt) == expected


# 2. Тесты для функции get_currency_rates
@patch('requests.get')
def test_get_currency_rates_success(mock_get):
    # Имитируем успешный ответ API
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"result": 90.50}

    with patch('os.getenv', return_value='test_key'):
        result = get_currency_rates(['USD'])
        assert result == [{"currency": "USD", "rate": 90.50}]


def test_get_currency_rates_no_api_key():
    with patch('os.getenv', return_value=None):
        # Нам нужно переинициализировать или подменить глобальную переменную API_KEY внутри теста
        with patch('src.views.API_KEY', None):
            assert get_currency_rates(['USD']) == []


@patch('requests.get')
def test_get_currency_rates_server_error(mock_get):
    """Тест: сервер API вернул 500 Internal Server Error"""
    mock_get.return_value.status_code = 500

    # Даже при ошибке сервера функция должна вернуть пустой список, а не вызвать исключение
    with patch('src.views.API_KEY', 'test_key'):
        result = get_currency_rates(['USD'])
        assert result == []


# 3. Тесты для функции get_stock_prices
@patch('yfinance.Ticker')
def test_get_stock_prices_success(mock_ticker):
    # Имитируем данные от yfinance
    mock_history = MagicMock()
    mock_history.empty = False
    mock_history.__getitem__.return_value.iloc = [-1]
    # Упрощенная имитация Series для Close цены
    mock_history['Close'].iloc = [150.00]

    mock_ticker.return_value.history.return_value = mock_history

    result = get_stock_prices(['AAPL'])
    assert result == [{"stock": "AAPL", "price": 150.0}]


@patch('yfinance.Ticker')
def test_get_stock_prices_not_found(mock_ticker):
    """Тест: тикер акции не существует"""
    # Имитируем пустую историю (empty=True)
    mock_history = MagicMock()
    mock_history.empty = True
    mock_ticker.return_value.history.return_value = mock_history

    result = get_stock_prices(['UNKNOWN'])
    # По логике кода, цена должна быть 0.0
    assert result == [{"stock": "UNKNOWN", "price": 0.0}]


# 4. Тест для  main_dashboard
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock_prices')
@patch('builtins.open', new_callable=mock_open, read_data='{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}')
def test_main_dashboard(mock_file, mock_stocks, mock_rates):
    # Подготовка моков для внутренних вызовов
    mock_rates.return_value = [{"currency": "USD", "rate": 90.0}]
    mock_stocks.return_value = [{"stock": "AAPL", "price": 150.0}]

    # Создаем тестовый DataFrame
    data = {
        'Дата операции': ['13.03.2026 17:00:00'],
        'Сумма операции': [-1000.0],
        'Номер карты': ['*1234'],
        'Категория': ['Еда'],
        'Описание': ['Магазин']
    }
    df = pd.DataFrame(data)

    result_json = main_dashboard('2026-03-13 17:00:00', df)
    result = json.loads(result_json)
    assert result['greeting'] == "Добрый день"


@patch('builtins.open', new_callable=mock_open, read_data='{ "bad": json }')
def test_main_dashboard_corrupted_json(mock_file):
    df = pd.DataFrame(columns=['Дата операции', 'Сумма операции', 'Номер карты'])
    # Мы ожидаем, что функция вернет JSON, даже если настройки битые
    result_json = main_dashboard('2026-03-13 17:00:00', df)
    assert "greeting" in result_json


def test_main_dashboard_no_data_in_range():
    """Тест: в DataFrame нет данных за нужный месяц"""
    # Данные за февраль
    data = {'Дата операции': ['01.02.2026'], 'Сумма операции': [-100], 'Номер карты': ['*1111'], 'Категория': ['X'],
            'Описание': ['Y']}
    df = pd.DataFrame(data)

    # Запрашиваем март
    result_json = main_dashboard('2026-03-01 00:00:00', df)
    result = json.loads(result_json)

    # Списки должны быть пустыми, но структура JSON должна сохраниться
    assert result['cards'] == []
    assert result['top_transactions'] == []
