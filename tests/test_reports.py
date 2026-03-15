import os

import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_df():
    """
        Создает тестовый DataFrame с транзакциями.
        Содержит данные за разные месяцы для проверки фильтрации по датам.
    """
    return pd.DataFrame({
        'Дата операции': ['31.12.2021', '01.11.2021', '01.01.2021'],
        'Категория': ['Супермаркеты', 'Супермаркеты', 'Супермаркеты'],
        'Сумма операции': [-100, -200, -300]
    })


def test_spending_by_category_logic(sample_df):
    """
        Проверяет логику фильтрации трат по категории за последние 3 месяца.
        Убеждается, что транзакции вне диапазона 90 дней от заданной даты игнорируются.
    """
    # Тестируем фильтр за 90 дней от 31.12.2021
    # Должны войти декабрь и ноябрь, но не январь
    result = spending_by_category(sample_df, "Супермаркеты", "31.12.2021")
    assert len(result) == 2
    assert -300 not in result['Сумма операции'].values


def test_decorator_creates_json_file(sample_df):
    """
        Проверяет работу декоратора @report_to_file.
        Убеждается, что при вызове функции создается папка 'reports' и в ней появляется JSON-файл.
    """
    # очисткa папки reports
    reports_path = os.path.join(os.getcwd(), "reports")
    if os.path.exists(reports_path):
        for f in os.listdir(reports_path):
            os.remove(os.path.join(reports_path, f))

    # Имя файла для теста
    test_filename = "test_report_output.json"

    # Вызываем функцию (декоратор сработает)
    # Чтобы передать имя файла в декоратор в тесте,
    # можно временно переопределить функцию или просто проверить файл по умолчанию
    spending_by_category(sample_df, "Супермаркеты", "31.12.2021")

    # Проверяем корень проекта на наличие папки reports
    # Находим путь к папке reports относительно файла теста
    reports_path = os.path.join(os.getcwd(), "reports")

    assert os.path.exists(reports_path), "Папка reports не была создана"
    assert len(os.listdir(reports_path)) > 0, "Файл отчета не создался"


def test_json_serialization_no_error(sample_df):
    """Проверяет, что ошибка 'Timestamp is not JSON serializable' исправлена"""
    try:
        spending_by_category(sample_df, "Супермаркеты", "31.12.2021")
    except TypeError as e:
        pytest.fail(f"Декоратор все еще не умеет сериализовать Timestamp: {e}")
