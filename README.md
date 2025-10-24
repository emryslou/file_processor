# File Processor
文件处理器

# 功能描述
1. 配置支持 yml
2. 通知方式: 邮件
3. 日志记录: 支持 控制台 与 文件 记录
4. 文件处理器: 支持 多文件处理器
5. 文件下载, 上传，备份支持:
    ftp, sftp, ftp, local (本机目录)
6. 依据输入文件后缀，自动选择读取函数（excel, csv）

# 使用说明
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
    - name: ftp_store # 存储名称: 随意，但不能重复，不要出现特殊字符，格式为: 英文字母和下划线
      type: ftp # 存储类型: 支持 ftp，ftps, sftp, local (本地文件)
      root_path: /应用文件-xunlei/data/data # 根目录: 后面的目录会自动附加上这个目录， 切记
      host: 192.168.1.27
      port: 2121 # FTP端口
      user: admin
      password: 'Abcd1234'
      encoding: utf-8
    # - name: sftp_store # 存储名称
    #   type: sftp # 存储类型
    #   root_path: /vol2/@appshare/xunlei/data
    #   host: 192.168.1.27
    #   port: 22
    #   user: admin
    #   password: 'Abcd1234'
    #   encoding: utf-8
    # - name: ftps_store # 存储名称
    #   type: ftps # 存储类型
    #   root_path: /应用文件-xunlei/data/data
    #   host: 192.168.1.27
    #   port: 2121 # FTP端口
    #   user: admin
    #   password: 'Abcd1234'
    #   encoding: utf-8
    # - name: local_store # 存储名称
    #   type: local # 存储类型
    #   root_path: data/ # 根目录
  processors:
    - driver: dram # 仅支持 dram, logic
      name: dram_processor
      dl_path: # 下载路径
        store: sftp/sftp_store # 存储: 存储类型/存储名称, stores 中 {type}/{name}
        path: dram/dl # 具体路径, 相对路径，实际为 {store的root_path}/{这里定义的路径}
      bak_path: # 备份路径，
        store: sftp/sftp_store # 存储类型/存储名称，最好和 dl_path 一致
        path: dram/bak # 备份路径
      ul_path: # 上传路径
        store: sftp/sftp_store # 存储类型/存储名称
        path: dram/upload # 上传路径
      proc_types: # 处理类型
        - type: t7_code # T7Code文件处理
          filter: 'COA*.xlsx' # 匹配COA*.xlsx文件
        - type: coa # COA文件处理
          filter: 'COA*.xlsx' # 匹配COA*.xlsx文件
        - type: apc # APC文件处理
          filter: '*APC*.xlsx' # 匹配*APC*.xlsx文件 
    - driver: logic # logic
      name: logic_processor # 逻辑处理器
      dl_path: 
        store: ftp/ftp_store # 本机存储/存储名称
        path: logic/dl # 下载路径
      ul_path: 
        store: ftp/ftp_store # 本机存储/存储名称
        path: logic/upload # 上传路径
      bak_path: 
        store: ftp/ftp_store # 本机存储/存储名称
        path: logic/bak # 备份路径
      proc_types: # 处理类型
        - type: t7_code # T7Code文件处理
          filter: 'T7Code*.xlsx' # 匹配T7Code*.xlsx文件
        - type: coa # COA文件处理
          filter: 'T7Code*.xlsx' # 匹配T7Code*.xlsx文件
        - type: apc # APC文件处理
          filter: 'APC*.xlsx' # 匹配APC*.xlsx文件
  logger: # 保持现状即可
    log_level: info
    log_file: data/log/file_processor.log
    log_rotate: 10 MB
    log_backtrace: true
  
  notification: # 通知
    - type: email  # 固定
      subject: "文件处理报告"     # 邮件主题
      sender: "emrys.liu@foxmail.com"  # 发送者邮箱
      recipients:                       # 接收者邮箱列表
        - "emrys.liu@foxmail.com"
        # - "recipient2@example.com"
      smtp_server: "smtp.qq.com"   # SMTP服务器地址
      smtp_port: 465                    # SMTP服务器端口
      smtp_username: "emrys.liu@foxmail.com"  # SMTP用户名
      smtp_password: "xxxxx"    # SMTP密码或授权码
```
