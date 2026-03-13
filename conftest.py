import pandas as pd
import pytest


@pytest.fixture
def temp_excel_file(tmp_path):
    """Создает временный корректный Excel-файл для тестов."""
    file_path = tmp_path / "test_data.xlsx"
    data = {
        'Дата операции': ['01.01.2023', '02.01.2023'],
        'Сумма операции': [-100.50, 500.00],
        'Номер карты': ['*1111', '*2222']
    }
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    return str(file_path)
