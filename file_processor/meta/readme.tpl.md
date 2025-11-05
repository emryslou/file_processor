# File Processor

## 功能描述
{{meta/changelog.md#功能描述}}

## 版本更新
{{meta/changelog.md#版本更新}}

## 项目结构
```
{{meta/package_structure}}
```

## 使用说明
1. 系统组件需求: Python >= 3.9
2. 建议安装 Python 3.11 环境， 下面是下载地址:
   - x64: https://www.python.org/ftp/python/3.11.1/python-3.11.1-amd64.exe
   - x86: https://www.python.org/ftp/python/3.11.1/python-3.11.1.exe 
3. 打开命令行，执行: `python -V`, 输出版本号，即安装成功
4. 打开命令行，执行: `python -m pip -V` 输出版本号，即安装成功
5. 全新安装`python -m pip install X:\your\path\xxxx.whl`, 出现安装成功即可
6. 更新安装`python -m pip install -U X:\your\path\xxxx.whl`, 出现安装成功即可
7. 验证: `python -m file_processor --help` 输出如下内容即为安装成功
```shell
Usage: python -m file_processor [OPTIONS]

Options:
  -c, --config PATH  配置文件路径  [required]
  --help             Show this message and exit
```
7. 配置定时任务，需要的路径 `python -m file_processor -c {你的配置文件路径}`，
  Window: `python -m file_processor -c X:\your\path\proc.yml`
  Linux: `python -m file_processor -c /your/path/proc.yml`  
8. 配置内容可参考 `proc.yml`
9. 脚本会在当前执行目录中自动创建 `data` 目录，其中 `tmp` 临时需要下载的文件，`log` 下面为日志文件（脚本执行异常时可做排查问题用）
9. 配置文件说明:
```yml
{{meta/example.yml}}
```
