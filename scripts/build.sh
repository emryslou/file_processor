dirname=$(dirname $(dirname $(readlink -f $0)))
project_name=$(basename $dirname)

tree $dirname -I dist -I __pycache__ -I dist -I build -I *.egg-info -I config -I data -I *.log > $dirname/package_structure.txt
sed -i "s#$dirname#$project_name#g" $dirname/package_structure.txt > $dirname/$project_name.txt
rm $dirname/$project_name.txt
python $dirname/setup.py bdist_wheel --dist-dir $dirname/dist
