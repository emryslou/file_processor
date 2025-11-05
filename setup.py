from setuptools import setup, find_packages
import os
from file_processor import __version__, __author__, __author_email__



# 确保当前目录正确
here = os.path.abspath(os.path.dirname(__file__))

setup(
    name="file_processor",
    version=__version__,
    author=__author__,
    author_email=__author_email__,  # 修复邮箱地址格式错误
    description="文件处理",
    long_description="""Demo""",
    long_description_content_type="text/markdown",
    url="https://github.com/emryslou/file_processor",  # 替换为实际仓库地址
    packages=[
        'file_processor',
        'file_processor.notification',
        'file_processor.processors',
        'file_processor.stores',
        'file_processor.utils'
    ],  # 显式列出所有包
    include_package_data=True,
    # 明确指定包数据
    package_data={
        '': ['*.md', '*.txt', '*.yml'],  # 包含根目录下的所有md和txt文件
    },
    # 指定额外的数据文件
    data_files=[
        # 安装readme.md和changelog.md到文档目录
        # 确保在Windows上也能正确处理路径
    ],
    install_requires=[
        'click == 8.3.0',
        'numpy >= 1.24.0, < 2.0.0',  # 添加numpy依赖并指定版本范围
        'pandas >= 2.1.4, < 3.0.0',  # 更新到与Python 3.11更兼容的pandas版本
        'openpyxl == 3.1.5',
        'loguru == 0.7.3',
        'pyyaml == 6.0.3',
        'paramiko == 4.0.0',
        'xlrd == 2.0.1',
    ],
    entry_points={
        "console_scripts": [
            "file_processor = file_processor.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',  # 更新Python版本要求以更好地支持依赖包
)

