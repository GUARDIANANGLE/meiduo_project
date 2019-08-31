# !/usr/bin/env python
# _*_ coding:utf-8 _*_
from django.conf import settings
from django.core.files.storage import Storage


class FastDFSStorage(Storage):

    def __init__(self):

        self.base_url = settings.FDFS_BASE_URL


    # 必写的函数
    def _open(self, name, mode='rb'):
        pass
    def _save(self, name, content, max_length=None):
        pass

    # 重写父类的 url函数 返回一个 IP:port/00/00/meizi.png 全路径
    def url(self, name):

    #         http://192.168.90.172:8888     +    /group1/M00/00/00/CtM3BVnihx-AKdf0AAPWWMjR7sE771.jpg

        return self.base_url + name

