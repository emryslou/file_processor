import pkgutil

def changelog() -> list[str]:
    """
    读取changelog.md文件内容，返回一个包含每个段落的字典列表。
    每个段落包含段落描述和段落内容。
    """
    blocks: list[dict] = []
    current_block: dict = {}
    for line in pkgutil.get_data('file_processor', 'meta/changelog.md').decode('utf-8').splitlines():
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

def desc() -> list[str]:
    """
    获取功能描述段落的内容。
    """
    return [block['content'] for block in changelog() if block['description'] == '功能描述'][0]

def version_update(version: str|None = None) -> list[str]:
    """
    获取指定版本的版本更新段落内容。
    如果未指定版本，返回所有版本更新段落内容。
    """
    contents: list[str] = [block['content'] for block in changelog() if block['description'] == '版本更新'][0]
    
    if not version:
        return contents
    
    version_tag = f'## {version}'
    ver_start = contents.index(version_tag)
    if ver_start == -1:
        return []
    
    ver_end = contents.index('## ', ver_start + 1) if '## ' in contents[ver_start + 1:] else len(contents)
    return contents[ver_start + 1:ver_end]

def package_structure() -> list[str]:
    """
    获取包结构段落。
    """
    return pkgutil.get_data('file_processor', 'meta/changelog.md').decode('utf-8').splitlines()