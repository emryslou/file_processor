import pytest

from file_processor.utils import tools
from datetime import datetime

def cases_valid_time_format():
    return [
        ('2025-11-12 12:13', datetime(year=2025, month=11, day=12, hour=12, minute=13), None),
        ('2025-11-12 12:13:12', datetime(year=2025, month=11, day=12, hour=12, minute=13, second=12), None),
        ('2025/11/12 12:13', datetime(year=2025, month=11, day=12, hour=12, minute=13), None),
        ('2025/11/12 12:13:12', datetime(year=2025, month=11, day=12, hour=12, minute=13, second=12), None),
        ('2025-11-12 12-12', datetime(year=2025, month=11, day=12, hour=12, minute=13, second=12), 1),
    ]

@pytest.mark.parametrize('_input,expect_value,err', cases_valid_time_format())
def test_valid_time_format(_input, expect_value, err):
    if err is not None:
        with pytest.raises(ValueError):
            tools.valid_time_format(_input)
    else:
        assert tools.valid_time_format(_input) == expect_value
    