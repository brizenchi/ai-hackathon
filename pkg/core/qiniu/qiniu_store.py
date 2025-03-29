from qiniu import Auth, put_file, etag
import qiniu.config
from typing import Tuple, Dict, Any
import os
from datetime import datetime

class QiniuStore:
    def __init__(self, access_key: str, secret_key: str, bucket_name: str,domain:str):
        self.auth = Auth(access_key, secret_key)
        self.bucket_name = bucket_name
        self.domain = domain
    def generate_key(self, file_path: str) -> str:
        """
        生成文件的存储键名
        :param file_path: 本地文件路径
        :return: 存储键名
        """
        # 使用时间戳和原始文件名组合生成唯一的key
        filename = os.path.basename(file_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{timestamp}_{filename}"

    def upload_file(self, local_file_path: str, key: str = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        上传文件到七牛云
        :param local_file_path: 本地文件路径
        :param key: 自定义的文件名，如果为None则自动生成
        :return: (是否成功, 文件URL或错误信息, 上传返回的详细信息)
        """
        try:
            if not os.path.exists(local_file_path):
                return False, "File not found", {}

            # 如果没有提供key，则自动生成
            if key is None:
                key = self.generate_key(local_file_path)

            # 生成上传凭证
            token = self.auth.upload_token(self.bucket_name, key, 3600)

            # 上传文件
            ret, info = put_file(token, key, local_file_path, version='v2')

            if info.status_code == 200:
                # 验证上传是否成功
                if ret['key'] == key and ret['hash'] == etag(local_file_path):
                    # 生成文件的公开URL（需要替换为你的七牛云域名）
                    file_url = f"{self.domain}/{key}"  # 替换为你的七牛云域名
                    return True, file_url, ret
                else:
                    return False, "Upload verification failed", ret
            else:
                return False, f"Upload failed: {info.error}", info.error

        except Exception as e:
            return False, f"Error during upload: {str(e)}", {}

    def get_file_url(self, key: str, expires: int = 3600) -> str:
        """
        获取文件的私有下载链接（如果是私有空间）
        :param key: 文件的key
        :param expires: 链接的有效期（秒）
        :return: 下载链接
        """
        base_url = f'{self.domain}/{key}'  # 替换为你的七牛云域名
        return self.auth.private_download_url(base_url, expires=expires)