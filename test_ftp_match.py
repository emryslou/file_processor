import fnmatch
from pathlib import Path

# 模拟FTP返回的文件列表
mock_files = [
    'data/file1.txt',
    'data/file2.csv',
    'data/report_2024.pdf',
    'data/image.jpg',
    'data/backup_20240101.zip',
    'data/backup_20240102.zip'
]

# 测试不同的匹配模式
test_patterns = [
    '*',           # 匹配所有文件
    '*.txt',       # 匹配所有txt文件
    '*.zip',       # 匹配所有zip文件
    'backup_*.zip', # 匹配所有备份zip文件
    'file?.csv',   # 匹配file后跟一个字符的csv文件
    'report_2024.*' # 匹配2024年的报告文件
]

print("测试FTPStore模糊匹配功能:")
print("="*50)

for pattern in test_patterns:
    # 使用我们实现的匹配逻辑
    matches = [Path(item) for item in mock_files if fnmatch.fnmatch(Path(item).name, pattern)]
    
    print(f"\n模式: '{pattern}'")
    print(f"匹配到的文件: {len(matches)} 个")
    for match in matches:
        print(f"  - {match}")