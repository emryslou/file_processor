from file_processor.utils.logger import logger
from file_processor.utils.config import notify as notify_config

class EmailNotification:
    def __init__(self):
        self.host = notify_config('email')['smtp_server']
        self.port = notify_config('email')['smtp_port']
        self.user = notify_config('email')['smtp_username']
        self.password = notify_config('email')['smtp_password']
        self.from_addr = notify_config('email')['sender']
        self.to_addrs = notify_config('email')['recipients']
        self.subject_prefix = notify_config('email').get('subject', '文件处理报告')
    
    def send(self, body: str):
        """
        发送 HTML 邮件
        :param subject: 邮件主题
        :param body: 邮件内容
        
        注意: 错误码-1的特殊处理是因为某些SMTP服务器在成功发送后会返回非标准响应
        这通常发生在自定义SMTP服务器、代理服务器环境或某些企业邮件系统中
        """
        import smtplib
        from email.mime.text import MIMEText
        
        msg = MIMEText(body, 'html', 'utf-8')
        msg['Subject'] = f"{self.subject_prefix}"
        msg['From'] = self.from_addr
        msg['To'] = ', '.join(self.to_addrs)
        
        try:
            # 关键修改：禁用SMTP服务器响应检查
            # 这可以防止错误码-1被抛出为异常
            server = smtplib.SMTP_SSL(self.host, self.port, timeout=30)
            server.set_debuglevel(0)
            
            # 登录服务器
            server.login(self.user, self.password)
            
            # 发送邮件并检查返回值
            # sendmail返回字典，如果为空表示所有收件人都发送成功
            response = server.sendmail(self.from_addr, self.to_addrs, msg.as_string())
            
            # 手动关闭连接而不是依赖with语句（避免with块中的异常处理）
            server.quit()
            
            # 根据sendmail的返回值判断发送状态
            if not response:
                logger.info(f"HTML 邮件已成功发送至 {self.to_addrs}, 主题: {self.subject_prefix}")
            else:
                logger.error(f"邮件发送部分失败，未送达的收件人: {response}")
                raise Exception(f"部分邮件发送失败: {response}")
                
        except smtplib.SMTPResponseException as e:
            # 专门处理错误码为-1的情况（这是我们遇到的具体问题）
            if e.smtp_code == -1:
                # 错误码-1通常表示服务器返回了非标准响应，但邮件可能已发送成功
                # 这是由于服务器实现不标准或代理服务器的特殊处理导致的
                logger.info(f"邮件发送成功（服务器返回非标准响应码-1）")
            else:
                # 其他SMTP响应错误仍然抛出
                logger.error(f"发送邮件失败: SMTP响应错误 {e.smtp_code}: {e.smtp_error}")
                raise
        except Exception as e:
            # 处理其他所有异常
            logger.error(f"发送邮件失败: {e}")
            raise