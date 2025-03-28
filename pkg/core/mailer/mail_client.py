from typing import Optional, List, Dict
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dataclasses import dataclass
from app.config.settings import settings
from email.utils import formataddr

logger = logging.getLogger(__name__)

@dataclass
class EmailConfig:
    """邮件配置"""
    host: str
    port: int
    username: str
    password: str
    sender_name: str
    use_ssl: bool = True
    timeout: int = 10
    
    def __init__(self, source_name: str = 'default'):
        """从settings初始化邮件配置"""
        config = settings.EMAIL.get(source_name)
        if not config:
            raise ValueError(f"Email config '{source_name}' not found in settings")
            
        self.host = config.get('host', 'smtp.gmail.com')
        self.port = config.get('port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
        self.use_ssl = config.get('use_ssl', True)
        self.timeout = config.get('timeout', 10)
        self.sender_name = config.get('sender_name', 'test')

class EmailClient:
    """邮件客户端"""
    _instances = {}

    def __new__(cls, source_name: str = 'default'):
        """单例模式"""
        if source_name not in cls._instances:
            cls._instances[source_name] = super().__new__(cls)
        return cls._instances[source_name]

    def __init__(self, source_name: str = 'default'):
        """初始化邮件客户端"""
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.source_name = source_name
            self.config = EmailConfig(source_name)
            self._smtp = None

    def _get_smtp(self) -> smtplib.SMTP:
        """获取SMTP连接"""
        if self._smtp is None:
            try:
                logger.info(f"Connecting to SMTP server: {self.config.host}:{self.config.port}")
                
                if self.config.use_ssl:
                    # 使用SSL连接
                    self._smtp = smtplib.SMTP_SSL(
                        self.config.host, 
                        self.config.port, 
                        timeout=self.config.timeout
                    )
                    logger.info("Using SSL connection")
                else:
                    # 使用普通连接并启用STARTTLS
                    self._smtp = smtplib.SMTP(
                        self.config.host, 
                        self.config.port, 
                        timeout=self.config.timeout
                    )
                    self._smtp.ehlo()
                    self._smtp.starttls()
                    self._smtp.ehlo()
                    logger.info("Using STARTTLS connection")

                # 登录前打印用户名（不打印密码）
                logger.info(f"Attempting login with username: {self.config.username}")
                self._smtp.login(self.config.username, self.config.password)
                logger.info("Successfully logged in to SMTP server")
                
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"Authentication failed: {e}")
                if self._smtp:
                    self._smtp.close()
                    self._smtp = None
                raise
            except smtplib.SMTPException as e:
                logger.error(f"SMTP error occurred: {e}")
                if self._smtp:
                    self._smtp.close()
                    self._smtp = None
                raise
            except Exception as e:
                logger.error(f"Failed to connect to SMTP server: {e}")
                if self._smtp:
                    self._smtp.close()
                    self._smtp = None
                raise

        return self._smtp

    async def send_email(
        self,
        to_addrs: List[str],
        subject: str,
        body: str,
        html: bool = False,
        cc: List[str] = None,
        bcc: List[str] = None,
        attachments: Dict[str, bytes] = None
    ) -> bool:
        """发送邮件"""
        try:
            msg = MIMEMultipart()
            # 使用 formataddr 设置发件人名称和地址
            msg['From'] = formataddr((self.config.sender_name, self.config.username))
            msg['To'] = ', '.join(to_addrs)
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)

            # 设置邮件内容
            content_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, content_type, 'utf-8'))

            # 添加附件
            if attachments:
                for filename, content in attachments.items():
                    attachment = MIMEText(content, 'base64', 'utf-8')
                    attachment["Content-Type"] = "application/octet-stream"
                    attachment["Content-Disposition"] = f'attachment; filename="{filename}"'
                    msg.attach(attachment)

            # 获取所有收件人
            all_recipients = to_addrs + (cc or []) + (bcc or [])

            # 发送邮件
            smtp = self._get_smtp()
            smtp.send_message(msg, from_addr=self.config.username, to_addrs=all_recipients)
            
            logger.info(f"Email sent successfully to {len(all_recipients)} recipients")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            # 如果发送失败，尝试重新建立连接
            self._smtp = None
            return False

    async def close(self):
        """关闭SMTP连接"""
        if self._smtp is not None:
            try:
                self._smtp.quit()
                self._smtp = None
                logger.info("SMTP connection closed")
            except Exception as e:
                logger.error(f"Error closing SMTP connection: {e}")
                self._smtp = None


