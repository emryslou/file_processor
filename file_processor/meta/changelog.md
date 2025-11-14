# 功能描述
1. 下载远程文件到本地
2. 处理文件
3. 上传处理后的文件到远程
4. 备份原始文件到远程
5. 支持 处理 xls, xlsx 文件
6. 支持存储类型: local (本地文件系统), ftp, ftps, sftp
7. 支持 处理 t7_code, coa, apc 等处理方式
8. 处理器: 支持 逻辑处理器 (logic) 和 内存处理器 (dram)

# 版本更新
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
