from .mail_client import EmailClient

class EmailFactory:
    """邮件客户端工厂"""
    _instances = {}
    
    @classmethod
    def get_instance(cls, source_name: str = 'default') -> EmailClient:
        """获取邮件客户端实例"""
        if source_name not in cls._instances:
            cls._instances[source_name] = EmailClient(source_name)
        return cls._instances[source_name] 