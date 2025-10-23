from file_processor.utils.logger import logger
import json
from .email import EmailNotification

def send_notification(notify_type: str, body: str):
    if notify_type == 'email':
        email_notifier = EmailNotification()
        email_notifier.send(body)
    else:
        logger.warning(f"未知的通知类型: {notify_type}")    

def gen_notification_body_html(result_info: dict) -> str:
    """
    基于cli.py中的日志处理逻辑，生成处理器结果的HTML网页
    
    Args:
        result_info: 包含处理器结果信息的字典，格式应与cli.py中处理的result_info一致
                    应包含'processor'键，值为各driver的处理结果字典
    
    Returns:
        str: 生成的HTML代码
    """
    html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>文件处理结果报告</title>
        <style>
            /* 全局样式 */
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f8f9fa;
                color: #333;
                line-height: 1.6;
            }
            
            /* 容器样式 */
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            }
            
            /* 标题样式 */
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 12px;
                margin-top: 0;
                font-weight: 600;
            }
            
            h2 {
                color: #34495e;
                margin-top: 25px;
                border-left: 5px solid #3498db;
                padding-left: 15px;
                font-weight: 500;
            }
            
            h3 {
                color: #555;
                margin-top: 20px;
                font-weight: 500;
            }
            
            /* 驱动部分 */
            .driver-section {
                margin-bottom: 35px;
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
            
            /* 状态标签 */
            .status-badge {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.85em;
                margin-left: 10px;
                vertical-align: middle;
            }
            
            /* 状态颜色 - 使用更柔和的色调 */
            .status-success {
                background-color: #e8f5e9;
                color: #2e7d32;
                border: 1px solid #c8e6c9;
            }
            
            .status-error {
                background-color: #ffebee;
                color: #c62828;
                border: 1px solid #ffcdd2;
            }
            
            .status-other {
                background-color: #fff8e1;
                color: #e65100;
                border: 1px solid #ffe082;
            }
            
            /* 表格样式 */
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            }
            
            th {
                background-color: #3498db;
                color: white;
                font-weight: 500;
                text-align: left;
                padding: 12px;
                border-bottom: 2px solid #2980b9;
            }
            
            td {
                border: 1px solid #ddd;
                padding: 10px 12px;
                text-align: left;
                vertical-align: top;
            }
            
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            
            tr:hover {
                background-color: #f1f1f1;
            }
            
            /* 文本样式 */
            p {
                margin-top: 15px;
                margin-bottom: 10px;
                color: #555;
            }
            
            /* 消息框样式 */
            .message-box {
                background-color: #e3f2fd;
                border-left: 4px solid #2196f3;
                padding: 15px 20px;
                margin: 15px 0;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }
            
            .message-box p {
                margin: 0;
                color: #1565c0;
                font-weight: 500;
            }
            
            .no-files {
                color: #777;
                font-style: italic;
                padding: 15px 0;
            }
            
            /* 文件列表 */
            .file-list {
                max-height: 120px;
                overflow-y: auto;
                background-color: #f1f3f4;
                padding: 15px;
                border-radius: 6px;
                font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
                font-size: 0.9em;
                border-left: 3px solid #3498db;
                word-break: break-all;
            }
            
            /* 状态单元格样式 - 避免整行显眼的绿色 */
            .status-cell {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 0.9em;
                font-weight: 500;
                display: inline-block;
            }
            
            .status-cell-success {
                background-color: #e8f5e9;
                color: #2e7d32;
            }
            
            .status-cell-error {
                background-color: #ffebee;
                color: #c62828;
            }
            
            /* 响应式调整 */
            @media (max-width: 768px) {
                .container {
                    padding: 15px;
                }
                
                h1 {
                    font-size: 1.8em;
                }
                
                h2 {
                    font-size: 1.5em;
                }
                
                table {
                    font-size: 0.9em;
                }
                
                th, td {
                    padding: 8px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>文件处理结果报告</h1>
    """
    
    # 遍历每个driver的处理结果
    for driver, result in result_info['processor'].items():
        # 根据状态选择不同的样式
        status_class = 'status-success' if result['status'] == 'success' else \
                       'status-error' if 'error' in result['status'] else 'status-other'
        
        # 显示处理消息
        message = result.get('message', '')
        html += f"""
        <div class="driver-section">
            <h2>
                处理 {driver}
                <span class="status-badge {status_class}">{result['status']}</span>
            </h2>
        """
        if message:
            html += f"""
            <div class="message-box">
            <p><strong>消息:</strong> {message}</p>
            </div>
            """
        
        # 遍历每种处理类型
        for proc_type, info in result['info'].items():
            html += f"""
            <h3>处理类型: {proc_type}, 匹配条件: {info['filter']}</h3>
            """
            
            find_files = info.get('files', {}).get('files', []) # info['files']['files']
            if len(find_files) == 0:
                html += "<div class='no-files'>未找到匹配文件</div>"
            else:
                html += f"""
                <p>共找到 {len(find_files)} 个匹配文件:</p>
                <div class='file-list'>{', '.join(str(f) for f in find_files)}</div>
                """
                
                # 显示成功处理的文件
                if len(info['files']['success']) > 0:
                    html += f"""
                    <p>成功处理 {len(info['files']['success'])} 个文件:</p>
                    <table>
                        <tr>
                            <th>输入文件</th>
                            <th>输出文件</th>
                        </tr>
                    """
                    for input_file, output_file in info['files']['success'].items():
                        html += f"""
                        <tr>
                            <td>{input_file}</td>
                            <td><span class='status-cell status-cell-success'>{output_file}</span></td>
                        </tr>
                        """
                    html += "</table>"
                
                # 显示处理失败的文件
                if len(info['files']['error']) > 0:
                    html += f"""
                    <p>处理失败 {len(info['files']['error'])} 个文件:</p>
                    <table>
                        <tr>
                            <th>文件路径</th>
                            <th>错误信息</th>
                        </tr>
                    """
                    for file, error in info['files']['error'].items():
                        html += f"""
                        <tr>
                            <td>{file}</td>
                            <td><span class='status-cell status-cell-error'>{error}</span></td>
                        </tr>
                        """
                    html += "</table>"
        
        html += "</div>"  # 结束driver-section
    
    # 结束HTML
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

# 示例用法：
# html_content = gen_notification_body_html(result_info)
# 然后可以将html_content保存到文件或通过邮件发送

def gen_notification_body_text(result_info: dict) -> str:
    """
    基于cli.py中的日志处理逻辑，生成处理器结果的纯文本报告
    
    Args:
        result_info: 包含处理器结果信息的字典，格式应与cli.py中处理的result_info一致
                    应包含'processor'键，值为各driver的处理结果字典
    
    Returns:
        str: 生成的纯文本报告
    """
    text_lines = []
    text_lines.append("="*80)
    text_lines.append("文件处理结果报告".center(80))
    text_lines.append("="*80)
    text_lines.append("")
    
    # 遍历每个driver的处理结果
    for driver, result in result_info['processor'].items():
        # 状态标识
        status_marker = "[成功]" if result['status'] == 'success' else \
                       "[错误]" if 'error' in result['status'] else "[其他]"
        
        text_lines.append(f"处理 {driver} {status_marker}: {result['status']}")
        text_lines.append("-"*80)
        
        # 遍历每种处理类型
        for proc_type, info in result['info'].items():
            text_lines.append(f"\n处理类型: {proc_type}, 匹配条件: {info['filter']}")
            text_lines.append("-"*40)
            
            find_files = info['files']['files']
            if len(find_files) == 0:
                text_lines.append("  未找到匹配文件")
            else:
                text_lines.append(f"  共找到 {len(find_files)} 个匹配文件:")
                # 文件列表可能很长，每个文件单独一行
                for file in find_files:
                    text_lines.append(f"    - {file}")
                
                # 显示成功处理的文件
                if len(info['files']['success']) > 0:
                    text_lines.append(f"\n  成功处理 {len(info['files']['success'])} 个文件:")
                    for file, status in info['files']['success'].items():
                        text_lines.append(f"    - {file}: {status}")
                
                # 显示处理失败的文件
                if len(info['files']['error']) > 0:
                    text_lines.append(f"\n  处理失败 {len(info['files']['error'])} 个文件:")
                    for file, error in info['files']['error'].items():
                        text_lines.append(f"    - {file}: {error}")
        
        text_lines.append("")  # 每个driver后空一行
    
    text_lines.append("="*80)
    
    return '\n'.join(text_lines)

# 示例用法：
# text_content = gen_notification_body_text(result_info)
# 然后可以将text_content保存到文件或通过邮件发送
    
    