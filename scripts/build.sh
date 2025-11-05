dirname=$(dirname $(dirname $(readlink -f $0)))
project_name=$(basename $dirname)

# 生成项目结构文件
tree $dirname -I dist -I __pycache__ -I dist -I build -I *.egg-info -I config -I data -I *.log > $dirname/$project_name/meta/package_structure.txt
sed -i "s#$dirname#$project_name#g" $dirname/$project_name/meta/package_structure.txt > $dirname/$project_name/meta/$project_name.txt
rm $dirname/$project_name/meta/$project_name.txt

# 创建 README.md 文件
cat $dirname/$project_name/meta/readme.tpl.md > $dirname/README.md
# 使用Python来处理文件替换，更安全地处理包含特殊字符的文本
python -c "
import scripts.tools as tools
import os

dirname = '$dirname'
project_name = '$project_name'

# 读取模板文件
with open(os.path.join(dirname, 'README.md'), 'r', encoding='utf-8') as f:
    content = f.read()

# 替换内容
# 功能描述
content = content.replace('{{meta/changelog.md#功能描述}}', '\n'.join(tools.read_changelog_desc()))
# 版本更新
content = content.replace('{{meta/changelog.md#版本更新}}', '\n'.join(tools.read_changelog_version_update()))
# example.yml
content = content.replace('{{meta/example.yml}}', tools.read_example_cfg())
# 项目结构
content = content.replace('{{meta/package_structure}}', tools.read_package_structure())

# 写回文件
with open(os.path.join(dirname, 'README.md'), 'w', encoding='utf-8') as f:
    f.write(content)
"

# python $dirname/setup.py bdist_wheel --dist-dir $dirname/dist
