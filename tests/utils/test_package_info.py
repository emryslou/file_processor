from file_processor.utils.package_info import changelog, desc as package_desc, version_update, package_structure, package_time
from file_processor import __version__

def test_changelog():
    """
    测试变更日志函数
    """
    info = changelog()
    assert info is not None, "changelog is None"
    assert len(info) > 0, "changelog is empty"
    assert info[0]['description'] == '功能描述', "changelog name error"
    assert len(info[0]['content']) > 0, "changelog content"


def test_desc():
    """
    测试描述函数
    """
    desc = package_desc()
    assert desc is not None, "desc is None"
    assert len(desc) > 0, "desc is empty"


def test_version_update():
    """
    测试版本更新函数
    """
    version = version_update()
    assert version is not None, "version is None"
    assert len(version) > 0, "version is empty"
    assert version[0] == f"## {__version__}", "version is not equal"


def test_package_structure():
    """
    测试包结构函数
    """
    import re
    package_info = package_structure()
    assert package_info is not None, "package_info is None"
    assert len(package_info) > 0, "package_info is empty"
    assert 'file_processor' == package_info[0], "first line not equal"
    assert re.match(fr'\d+ directories, \d+ files', package_info[-1]), "last line not match"


def test_package_time():
    """
    测试包时间函数
    """
    import re
    _time = package_time()
    assert _time is not None, "_time is None"
    assert re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', _time), "package time not match"
    