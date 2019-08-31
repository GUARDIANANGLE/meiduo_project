# !/usr/bin/env python
# _*_ coding:utf-8 _*_

# 1.导包 认证后端的包
from django.contrib.auth.backends import ModelBackend
import re
from .models import User

def get_user_by_account(account):

    try:
        # 4.校验username  又校验 手机号
        if re.match('^1[345789]\d{9}$', account):
            # 手机号
            user = User.objects.get(mobile=account)
        else:
            # username
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


# 2.类继承
class UsernameMobileAuthBackend(ModelBackend):

    # 3.重写父类的 authenticate函数
    def authenticate(self, request, username=None, password=None, **kwargs):

        user = get_user_by_account(username)

        # 验证码密码正确性
        if user and user.check_password(password):
            return user

# 5. dev.py 改后端认证的配置