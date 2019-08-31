from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
import re
from django import http

from meiduo_mall.settings.dev import logger


class RegisterView(View):
    # 1.注册页面显示
    def get(self, request):
        return render(request, 'register.html')

    # 2.注册功能
    def post(self, request):

        # 1. 接收解析参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')

        # 2. 校验参数
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseForbidden('缺少参数!')
        # *   1.用户名: ---------判空,正则校验,是否重复
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # *   2.密码:   --------- 判空,正则校验
        if not re.match('^^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # *   3.确认密码: ---------判空,判断是否相等
        if password2 != password:
            return http.HttpResponseForbidden('两次密码输入不一致')
        # *   4.手机号:---------   判空,正则校验,是否重复
        if not re.match('^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')

        # *   5.图形验证码:
        # *   6.短信验证码:

        # *   7.同意”美多商城用户使用协议“: 判断是否选中
        if allow != 'on':
            return http.HttpResponseForbidden('请求协议!')

        # 3. 注册用户
        try:
            from apps.users.models import User
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except Exception as e:
            logger.error(e)
            return render(request, 'register.html')

        # 4.保持登录状态: cookie ---session
        from django.contrib.auth import login
        login(request, user,backend=None)

        # 5. 重定向到首页
        return redirect(reverse('contents:index'))
