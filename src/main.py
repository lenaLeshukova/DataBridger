from utils import load_operations_from_excel
from views import main_dashboard


def run():
    # Загружаем данные, если папка data лежит в корне проекта, Python её не видит, поднимаемся на уровень выше.
    df = load_operations_from_excel('data/operations.xlsx')

    # Если df пустой или None, не идем дальше
    if df is None or df.empty:
        print("Критическая ошибка: Данные не загружены. Проверьте путь к файлу!")
        return


    # Передаем дату и DataFrame в основную функцию
    json_response = main_dashboard("2021-12-31 16:44:00", df)

    print(json_response)


if __name__ == "__main__":
    run()
