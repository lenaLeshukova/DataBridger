import json

import pandas as pd


def analyze_cashback_categories(data: list[dict], year: int, month: int) -> str:
    """
        Анализирует транзакции за конкретный месяц и год для расчета потенциального кешбэка.

        Функция фильтрует список транзакций по заданному периоду, группирует их по категориям
        и рассчитывает кешбэк (1% от суммы каждой операции). Результат сортируется
        по убыванию суммы кешбэка.

        Args:
            data (list[dict]): Список словарей с данными о транзакциях.
                Обязательные ключи: 'Дата операции', 'Категория', 'Сумма операции'.
            year (int): Год для анализа (например, 2021).
            month (int): Порядковый номер месяца для анализа (1-12).

        Returns:
            str: JSON-строка, где ключи — названия категорий,
                а значения — начисленный кешбэк (целые числа).

        Example:
            >>> analyze_cashback_categories(transactions, 2021, 12)
            '{"Супермаркеты": 150, "Аптеки": 20}'
        """
    analysis = {}

    for transaction in data:
        try:
            # Превращаем строку/объект даты в понятный формат
            date_obj = pd.to_datetime(transaction['Дата операции'], dayfirst=True)

            if date_obj.year == year and date_obj.month == month:
                category = transaction.get('Категория', 'Разное')
                # В Excel суммы отрицательные, берем модуль
                amount = abs(float(transaction.get('Сумма операции', 0)))
                # Считаем 1% кешбэка
                cashback = int(amount * 0.01)

                analysis[category] = analysis.get(category, 0) + cashback
        except Exception:
            continue  # Пропускаем пустые строки или ошибки формата

    # Сортируем по убыванию выгоды
    sorted_analysis = dict(sorted(analysis.items(), key=lambda item: item[1], reverse=True))
    return json.dumps(sorted_analysis, ensure_ascii=False, indent=4)
