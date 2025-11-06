dirname=$(dirname $(dirname $(readlink -f $0)))
project_name=$(basename $dirname)

# 生成项目结构文件
tree $dirname -I dist -I __pycache__ -I dist -I build -I *.egg-info -I config -I data -I *.log > $dirname/$project_name/meta/package_structure.txt
sed -i "s#$dirname#$project_name#g" $dirname/$project_name/meta/package_structure.txt > $dirname/$project_name/meta/$project_name.txt
rm $dirname/$project_name/meta/$project_name.txt

# 打包时间
python -c "import scripts.tools as tools; tools.generate_package_time()"

# 生成 README.md 文件
python -c "import scripts.tools as tools; tools.generate_readme()"


python $dirname/setup.py bdist_wheel --dist-dir $dirname/dist

# 删除打包时间文件
python -c "import scripts.tools as tools; tools.remove_package_time()"