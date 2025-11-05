dirname=$(dirname $(dirname $(readlink -f $0)))
project_name=$(basename $dirname)

# 生成项目结构文件
tree $dirname -I dist -I __pycache__ -I dist -I build -I *.egg-info -I config -I data -I *.log > $dirname/$project_name/meta/package_structure.txt
sed -i "s#$dirname#$project_name#g" $dirname/$project_name/meta/package_structure.txt > $dirname/$project_name/meta/$project_name.txt
rm $dirname/$project_name/meta/$project_name.txt

# 创建 README.md 文件
cat $dirname/$project_name/meta/readme.tpl.md > $dirname/README.md
# 使用Python来处理文件替换，更安全地处理包含特殊字符的文本

# 生成 README.md 文件
python -c "import scripts.tools as tools; tools.generate_readme()"


python $dirname/setup.py bdist_wheel --dist-dir $dirname/dist
