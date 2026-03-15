import pandas as pd


def load_operations_from_excel(file_path: str) -> pd.DataFrame:
    """Считывает данные из Excel и возвращает DataFrame."""
    try:
        # Читаем файл, указывая, что дата находится в первом столбце
        df = pd.read_excel(file_path, engine='openpyxl')
        # Преобразуем колонку с датой в формат datetime для расчетов
        df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)
        return df
    except Exception as e:
        print(f"Ошибка при чтении Excel: {e}")
        return pd.DataFrame()
