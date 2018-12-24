from django.core.files.storage import Storage
from django.conf import settings
from django.utils.deconstruct import deconstructible

from fdfs_client.client import Fdfs_client


@deconstructible
class FDFSStorage(Storage):
    """自定义FDFS文件存储类"""
    def __init__(self, client_conf=None, base_url=None):
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF

        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.FDFS_NGINX_URL

        self.base_url = base_url

    def _save(self, name, content):
        """
        name: 上传文件的名称: 1.jpg
        content: 包含上传文件内容的File对象，content.read()获取上传文件的内容
        """
        # 将文件上传到FDFS文件存储系统
        # client = Fdfs_client('客户端配置文件路径')
        client = Fdfs_client(self.client_conf)
        res = client.upload_by_buffer(content.read())

        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件到FDFS系统失败')

        # 获取上传文件的id
        file_id = res.get('Remote file_id')
        return file_id

    def exists(self, name):
        """
        在调用_save保存文件之前，会先调用此方法判断上传的文件名称和文件系统中原有的文件名是否冲突
        name: 上传文件的名称: 1.jpg
        """
        return False

    def url(self, name):
        """
        返回可访问到文件存储系统中文件完整url路径
        name: 数据库表中图片字段存储的内容(文件id)
        """
        return self.base_url + name

