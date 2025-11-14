# File Processor

## 功能描述
1. 下载远程文件到本地
2. 处理文件
3. 上传处理后的文件到远程
4. 备份原始文件到远程
5. 支持 处理 xls, xlsx 文件
6. 支持存储类型: local (本地文件系统), ftp, ftps, sftp
7. 支持 处理 t7_code, coa, apc 等处理方式
8. 处理器: 支持 逻辑处理器 (logic) 和 内存处理器 (dram)


## 版本更新
## 0.0.3-rc2
1. Issue Fix: T7Code（dram & logic）文件转换为xls时，要使用xlwt引擎，在某些场景下可能文件没法使用 @dukang

## 0.0.3-rc1
1. Issue Fix: apc文件的第一列日期时间格式，要去掉秒， 不管dram还是logic @dukang

## 0.0.3-rc0
1. 更新 example.yml 配置文件 @emrys.liu
2. Fix: logic的COA文件中的wafer ID，需要的格式是KPB425_02，不是KPB425#02 @dukang
3. Fix: logic的APC文件，REPLY_DTTS对应的日期，要和Dram一样，是2025/9/29 03:43:00这种，不要自定义的2025-09-29 03:43:00 @dukang

## 0.0.3-dev
1. 支持多个命令: run -- 处理文件；package-info 显示包信息
2. 处理器 dram.coa 第一列数据用 LOT_ID 替换数据 mother lot 9位
3. 处理器 logic.coa 第一列数据用 增加 Lot ID 前缀

## 0.0.2-rc2
1. 修复 store 资源回收问题

## 0.0.2-rc1
1. 修改 dram apc: lot_id 取值方式
2. logic apc: subtitle_id 计算方式优化
3. 支持 处理 xls 文件

## 项目结构
```
file_processor
├── LICENSE
├── README.md
├── file_processor
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── meta
│   │   ├── __init__,py
│   │   ├── changelog.md
│   │   ├── example.yml
│   │   ├── package_structure.txt
│   │   └── readme.tpl.md
│   ├── notification
│   │   ├── __init__.py
│   │   └── email.py
│   ├── processors
│   │   ├── __init__.py
│   │   ├── dram.py
│   │   └── logic.py
│   ├── stores
│   │   ├── __init__.py
│   │   ├── ftp.py
│   │   ├── ftps.py
│   │   ├── local.py
│   │   ├── sftp.py
│   │   └── store.py
│   └── utils
│       ├── __init__.py
│       ├── config.py
│       ├── logger.py
│       └── package_info.py
├── scripts
│   ├── build.sh
│   ├── proxy.sh
│   ├── shell_env.init.sh
│   └── tools.py
├── setup.py
└── tests
    ├── meta
    ├── test_ftp_match.py
    └── utils

11 directories, 31 files

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
version: 1.0.0
app:
  stores: # 存储配置
    - name: ftp_store # 存储名称 -------------------------------- FTP Start ----------------------------
      type: ftp # 可选项: local, ftp, ftps, sftp
      root_path: /path
      host: 192.168.1.27
      port: 2121 # FTP端口
      user: admin
      password: 'password'
      encoding: utf-8 # -------------------------------- FTP End ----------------------------
    - name: sftp_store # 存储名称 -------------------------------- SFTP Start ----------------------------
      type: sftp # 存储类型
      root_path: /vol2/@appshare/xunlei/data/data
      host: 192.168.1.27
      port: 22
      user: admin
      password: 'Abcd1234'
      encoding: utf-8 # -------------------------------- SFTP End ----------------------------
    - name: ftps_store # 存储名称 -------------------------------- FTPS Start ----------------------------
      type: ftps # 存储类型
      root_path: /应用文件-xunlei/data/data
      host: 192.168.1.27
      port: 2121 # FTP端口
      user: admin
      password: 'Abcd1234'
      encoding: utf-8 # -------------------------------- FTPS End ----------------------------  
    - name: local_store # 存储名称 -------------------------------- Local Start ----------------------------
      type: local # 存储类型
      root_path: data/ # 根目录 # -------------------------------- Local End ----------------------------
  processors:
    - driver: dram # 处理器驱动, dram 或 logic -------------------------------- Dram Start ----------------------------
      name: dram_processor
      dl_path: # 下载路径, 或被覆盖或者指定
        store: ftps/ftps_store # 存储类型/存储名称
        path: dram/dl # 下载路径
      bak_path: # 备份路径
        store: ftps/ftps_store # 存储类型/存储名称
        path: dram/bak # 备份路径
      ul_path: # 上传路径, 或被覆盖或者指定
        store: ftps/ftps_store # 存储类型/存储名称
        path: dram/upload # 上传路径, 或被覆盖或者指定
      proc_types: # 处理类型
        - type: t7_code # T7Code文件处理
          filter: 't7_code*.xlsx' # 匹配t7_code*.xlsx文件
          dl_path: dram/dl/t7_code # 下载路径, 或被覆盖或者指定
          ul_path: dram/upload/t7_code
        - type: coa # COA文件处理
          filter: 'COA*.xlsx' # 匹配COA*.xlsx文件
          dl_path: dram/dl/coa # 下载路径, 或被覆盖或者指定 
          ul_path: dram/upload/coa
        - type: apc # APC文件处理
          filter: '*APC*.xlsx' # 匹配*APC*.xlsx文件
          dl_path: dram/dl/apc # 下载路径, 或被覆盖或者指定 
          ul_path: dram/upload/apc # 上传路径 ，相对于 store.root_path, 会覆盖 url.path ----- -------------------------------- Dram End ----------------------------
    - driver: logic # 处理器驱动, dram 或 logic -------------------------------- Logic Start ----------------------------
      name: logic_processor # 逻辑处理器
      dl_path: 
        store: ftp/ftp_store # 本机存储/存储名称
        path: logic/dl # 下载路径
        dl_path: dram/dl/coa # 下载路径, 或被覆盖或者指定 
        ul_path: dram/upload/coa # 上传路径, 或被覆盖或者指定
      ul_path: 
        store: ftp/ftp_store # 本机存储/存储名称
        path: logic/upload # 上传路径
        dl_path: dram/dl/coa # 下载路径, 或被覆盖或者指定 
        ul_path: dram/upload/coa # 上传路径, 或被覆盖或者指定
      bak_path: 
        store: ftp/ftp_store # 本机存储/存储名称
        path: logic/bak # 备份路径
        dl_path: dram/dl/coa # 下载路径, 或被覆盖或者指定 
        ul_path: dram/upload/coa # 上传路径, 或被覆盖或者指定
      proc_types: # 处理类型
        - type: t7_code # T7Code文件处理
          filter: 'T7Code*.xlsx' # 匹配T7Code*.xlsx文件
          dl_path: dram/dl/t7_code # 下载路径, 或被覆盖或者指定
          ul_path: dram/upload/t7_code
        - type: coa # COA文件处理
          filter: 'COA*.xlsx' # 匹配COA*.xlsx文件
          dl_path: dram/dl/coa # 下载路径, 或被覆盖或者指定 
          ul_path: dram/upload/coa
        - type: apc # APC文件处理
          filter: 'APC*.xlsx' # 匹配APC*.xlsx文件
          dl_path: dram/dl/apc # 下载路径, 或被覆盖或者指定 
          ul_path: dram/upload/apc # 上传路径 ，相对于 store.root_path, 会覆盖 url.path -------------------------------- Logic End ----------------------------
  logger:
    log_level: debug
    log_file: data/log/file_processor.log
    log_rotate: 10 MB
    log_backtrace: true
    console_output: true
  notification:
    - type: email      
      subject: "文件处理报告"     # 邮件主题
      sender: "emrys.liu@foxmail.com"  # 发送者邮箱
      recipients:                       # 接收者邮箱列表
        - "emrys.liu@foxmail.com"
        # - "recipient2@example.com"
      smtp_server: "smtp.qq.com"   # SMTP服务器地址
      smtp_port: 465                    # SMTP服务器端口
      smtp_username: "emrys.liu@foxmail.com"  # SMTP用户名
      smtp_password: "password_or_authorization_code"    # SMTP密码或授权码
```
