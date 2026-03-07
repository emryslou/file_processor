from file_processor.processors.data_pipe import *
import pytest

def test_data_format():
    assert DataFormat.XLSX.get_file_extension() == 'xlsx'
    assert DataFormat.XLS.get_file_extension() == 'xls'
    assert DataFormat.CSV.get_file_extension() == 'csv'
    assert DataFormat.match_file_format('test.xlsx') == DataFormat.XLSX
    assert DataFormat.match_file_format('test.xls') == DataFormat.XLS
    assert DataFormat.match_file_format('test.csv') == DataFormat.CSV
    assert DataFormat.get_all_file_extensions() == ['xlsx', 'xls', 'csv']
    assert DataFormat.is_supported('test.xlsx') == True
    assert DataFormat.is_supported('test.xls') == True
    assert DataFormat.is_supported('test.csv') == True
    assert DataFormat.is_supported('test.txt') == False

    with pytest.raises(ValueError):
        DataFormat.match_file_format('test.txt')
