import pandas as pd

from src.utils import load_operations_from_excel


# 1. Тест успешной загрузки
def test_load_operations_success(temp_excel_file):
    """Проверяет, что данные загружаются и дата конвертируется в datetime."""
    df = load_operations_from_excel(temp_excel_file)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) == 2
    # Проверяем, что тип колонки с датой изменился на datetime
    assert pd.api.types.is_datetime64_any_dtype(df['Дата операции'])


# 2. Тест: файл не найден
def test_load_operations_file_not_found():
    """Проверяет, что при отсутствии файла возвращается пустой DataFrame."""
    # Передаем путь к несуществующему файлу
    df = load_operations_from_excel("non_existent_file.xlsx")

    assert isinstance(df, pd.DataFrame)
    assert df.empty


# 3. Тест: файл поврежден или пуст
def test_load_operations_corrupted_file(tmp_path):
    """Проверяет обработку ошибок, если файл не является валидным Excel."""
    bad_file = tmp_path / "broken.xlsx"
    bad_file.write_text("Это не эксель, а просто текст")

    df = load_operations_from_excel(str(bad_file))

    assert isinstance(df, pd.DataFrame)
    assert df.empty
