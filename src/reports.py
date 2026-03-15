import json
import os
from datetime import datetime, timedelta
from functools import wraps

import pandas as pd


def report_to_file(filename=None):
    """
        Декоратор для автоматического сохранения результата функции в JSON-файл.
        Создает директорию 'reports' в корне проекта, если она отсутствует.
        """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Создаем папку reports в корне
            reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
            os.makedirs(reports_dir, exist_ok=True)

            file_name = filename if isinstance(filename,
                                               str) else f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = os.path.join(reports_dir, file_name)

            # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Конвертируем DataFrame в JSON-совместимый список
            if isinstance(result, pd.DataFrame):
                # .to_json правильно обрабатывает Timestamp, превращая их в строки
                data_to_save = json.loads(result.to_json(orient='records', date_format='iso'))
            else:
                data_to_save = result

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)

            return result

        return wrapper

    if callable(filename):
        return decorator(filename)
    return decorator


@report_to_file
def spending_by_category(transactions: pd.DataFrame, category: str, date: str = None) -> pd.DataFrame:
    """
        Формирует отчет по тратам в заданной категории за последние 3 месяца.

        Args:
            transactions (pd.DataFrame): Датафрейм с транзакциями.
            category (str): Название категории для фильтрации.
            date (str, optional): Дата окончания периода (ДД.ММ.ГГГГ).
                Если не указана, используется текущая дата.

        Returns:
            pd.DataFrame: Отфильтрованные транзакции за 90 дней.
        """
    target_date = pd.to_datetime(date, dayfirst=True) if date else pd.Timestamp.now()
    start_date = target_date - timedelta(days=90)

    df = transactions.copy()
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)

    # Фильтруем по категории и по датам
    filtered = df[(df['Категория'] == category) &
                  (df['Дата операции'] <= target_date) &
                  (df['Дата операции'] >= start_date)]
    return filtered
