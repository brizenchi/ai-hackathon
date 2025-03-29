from qiniu import Auth, put_file, etag
import qiniu.config
from typing import Tuple, Dict, Any
import os
from datetime import datetime
from app.config.settings import settings
from pkg.core.qiniu.qiniu_store import QiniuStore
class QiniuFactory:
    _instances = {}
    def __init__(self):
        if self not in self._instances:
            access_key = settings.QINIU_ACCESS_KEY
            secret_key = settings.QINIU_SECRET_KEY
            bucket_name = settings.QINIU_BUCKET_NAME
            domain = settings.QINIU_DOMAIN
            self.qiniu_store = QiniuStore(access_key, secret_key, bucket_name,domain)
            self._instances[self] = self.qiniu_store

    def get_qiniu_store(self):
        return self.qiniu_store
