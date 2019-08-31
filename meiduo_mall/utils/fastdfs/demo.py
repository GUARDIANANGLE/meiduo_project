# !/usr/bin/env python
# _*_ coding:utf-8 _*_


# 1.导包
from fdfs_client.client import Fdfs_client

# 2.实例化
client = Fdfs_client('client.conf')

# 3.上传图片
re = client.upload_by_filename('/Users/lpf/Desktop/meizi.png')

print(re)