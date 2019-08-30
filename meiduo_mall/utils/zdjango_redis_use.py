# !/usr/bin/env python
# _*_ coding:utf-8 _*_


def demo():
    # 1.导包
    from django_redis import get_redis_connection

    # 2.链接数据库
    client = get_redis_connection('default')

    # 3.增删改查
    client.set('django_redis_key', 'meiduo')

    result = client.get('django_redis_key')

    # 千万注意: 取出redis的数据类型是 bytes
    print(result)


