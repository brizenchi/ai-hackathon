from typing import Optional, List, Dict

import logging
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import smtplib

project_root = str(Path(__file__).parent.parent.parent.parent)
sys.path.append(project_root)
# 加载环境变量（在导入其他模块之前）
env = os.getenv("APP_ENV", "dev")
env_file = os.path.join(project_root, "deployment", f".env.{env}" if env != "dev" else ".env")

load_dotenv(env_file)

from pkg.core.mailer.mail_factory import EmailFactory


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

async def test_send_email():
    """测试发送邮件"""
    try:
        # 打印完整的配置信息（除了密码）
        logger.info("Email Configuration:")
        logger.info(f"Environment: {env}")
        logger.info(f"Config file: {env_file}")
        logger.info(f"Host: {os.getenv('EMAIL_HOST')}")
        logger.info(f"Port: {os.getenv('EMAIL_PORT')}")
        logger.info(f"Username: {os.getenv('EMAIL_USERNAME')}")
        logger.info(f"Sender Name: {os.getenv('EMAIL_SENDER_NAME')}")
        logger.info(f"Use SSL: {os.getenv('EMAIL_USE_SSL')}")
        logger.info(f"Timeout: {os.getenv('EMAIL_TIMEOUT')}")
        
        email_client = EmailFactory.get_instance()
        
        # 发送测试邮件
        success = await email_client.send_email(
            to_addrs=['kuniseichi@gmail.com'],
            subject='Test Email from Newsletter Service',
            body="""
            <h1>Test Email</h1>
            <p>This is a test email from the newsletter service.</p>
            <p>If you receive this email, the email service is working correctly.</p>
            """,
            html=True,
            attachments={'test.txt': b'Hello World'}
        )
        
        if success:
            logger.info("✅ Email sent successfully!")
        else:
            logger.error("❌ Failed to send email")
            
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ Authentication failed: {e}", exc_info=True)
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP error: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}", exc_info=True)
    finally:
        # 关闭连接
        await email_client.close()

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_send_email())
