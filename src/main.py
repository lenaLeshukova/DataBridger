import os

from src.reports import spending_by_category
from src.services import analyze_cashback_categories
from src.utils import load_operations_from_excel


def main():
    # 1. Настройка путей
    base_dir = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(base_dir, '..', 'data', 'operations.xlsx')

    # 2. Загрузка данных
    print("Загрузка данных...")
    df = load_operations_from_excel(excel_path)

    # Преобразуем DataFrame в список словарей для модуля services
    transactions_list = df.to_dict(orient='records')

    # 3. Работа с модулем SERVICES (Выгодные категории)
    print("\n--- Анализ кешбэка за декабрь 2021 ---")
    cashback_json = analyze_cashback_categories(transactions_list, 2021, 12)
    print(cashback_json)

    # 4. Работа с модулем REPORTS (Траты по категории)
    print("\n--- Генерация отчета по категории 'Супермаркеты' ---")
    # Отчет автоматически сохранится в папку /reports благодаря декоратору
    report_df = spending_by_category(df, "Супермаркеты", "31.12.2021")

    print(f"Отчет сформирован. Найдено транзакций: {len(report_df)}")
    print(report_df.head())


if __name__ == "__main__":
    main()
