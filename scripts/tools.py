import os

ROOT_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
PROJECT_PATH = os.path.join(ROOT_PATH, 'file_processor')
META_PATH = os.path.join(PROJECT_PATH, 'meta')


def read_changelog():
    """读取changelog.md文件
    处理算法:
    1. 读取文件内容
    2. 按行遍历文件内容
    3. 若行以 '# ' 开头, 表示新的记录kuai块, 则将当前记录块添加到 blocks 中, 并创建新的记录块
    4. 如果非 '# ' 开头, 则将行添加到当前记录块的描述中，直到遇到下一个 '# ' 开头的行


    Returns:
        list[dict]: 每个版本的变更记录
    """
    blocks: list[dict] = []
    current_block: dict = {}
    
    with open(os.path.join(META_PATH, 'changelog.md'), 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('# '):
                if current_block:
                    blocks.append(current_block)
                current_block = {'description': line[2:], 'content': []}
            elif current_block:
                current_block['content'].append(line)
    
    if current_block:
        blocks.append(current_block)
    
    return blocks

def read_changelog_desc():
    """读取changelog.md文件中的描述部分
    """
    blocks = read_changelog()
    return [block['content'] for block in blocks if block['description'] == '功能描述'][0]

def read_changelog_version_update(version: str|None = None):
    """读取changelog.md文件中的版本号部分
    """
    blocks = read_changelog()
    contents: list[str] = [block['content'] for block in blocks if block['description'] == '版本更新'][0]
    if not version:
        return contents
    
    version_tag = f'## {version}'
    ver_start = contents.index(version_tag)
    if ver_start == -1:
        return []

    sub_content: list[str] = []
    for lint in contents[ver_start + 1:]:
        if lint.startswith('## '):
            break
        sub_content.append(lint)
    
    return sub_content

def read_example_cfg():
    """读取example.yml文件内容
    """
    with open(os.path.join(META_PATH, 'example.yml'), 'r', encoding='utf-8') as f:
        return f.read()

def read_package_structure():
    """读取package_structure文件内容
    """
    with open(os.path.join(META_PATH, 'package_structure.txt'), 'r', encoding='utf-8') as f:
        return f.read()

def generate_readme():
    """生成README.md文件
    """
    with open(os.path.join(META_PATH, 'readme.tpl.md'), 'r', encoding='utf-8') as f:
        content = f.read()

    # 功能描述
    content = content.replace('{{meta/changelog.md#功能描述}}', '\n'.join(read_changelog_desc()))
    # 版本更新
    content = content.replace('{{meta/changelog.md#版本更新}}', '\n'.join(read_changelog_version_update()))
    # example.yml
    content = content.replace('{{meta/example.yml}}', read_example_cfg())
    # 项目结构
    content = content.replace('{{meta/package_structure}}', read_package_structure())

    # 写回文件
    with open(os.path.join(ROOT_PATH, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(content)


if __name__ == '__main__':
    import sys

    sub_cmd = 'generate_readme'
    if len(sys.argv) > 1:
        sub_cmd = sys.argv[1]
    match sub_cmd:
        case 'generate_readme':
            print('generate_readme')
            generate_readme()
        case _:
            print(f'Unknown sub command: {sub_cmd}')