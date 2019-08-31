from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from QQLoginTool.QQtool import OAuthQQ

from apps.oauth.models import OAuthQQUser
from apps.users.models import User
from utils.response_code import RETCODE


# 是否绑定openid
from utils.secret import SecretOauth


def is_bind_openid(openid, request):
    try:
        # 1. 如果 数据表里面啊存在 --绑过了
        oauth_user = OAuthQQUser.objects.get(openid=openid)

    except Exception as e:
        # 2. 不存在 没有绑定过
        print(openid)
        openid = SecretOauth().dumps({'openid':openid})

        return render(request, 'oauth_callback.html',context={'openid':openid})
    else:
        user = oauth_user.user

        # 保持登录状态
        login(request, user)

        # 设置首页用户名
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=24 * 14 * 3600)
        # 重定向 首页

        return response


class QQAuthView(View):
    def get(self, request):
        # 1. 解析参数  code
        code = request.GET.get('code')

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        # 2. code-->token
        token = oauth.get_access_token(code)

        # 3. token--->openid
        openid = oauth.get_open_id(token)

        # 4.是否绑定openid 校验
        response = is_bind_openid(openid, request)
        return response

    def post(self,request):
        # 1.接收参数
        mobile = request.POST.get('mobile')
        pwd = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        openid = request.POST.get('openid')


        # 解密openid
        openid = SecretOauth().loads(openid).get('openid')
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})

        # 2.判空正则校验 图片验证 短信验证呢
        # 3. 判断 user是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except Exception as e:
            # 没注册--新注册一个
            user = User.objects.create_user(username=mobile,mobile=mobile,password=pwd)
        else:
            # 校验密码
            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})


        # 4. 绑定openid
        try:
            OAuthQQUser.objects.create(user=user,openid=openid)
        except Exception as e:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})

        # 5.重定向到 首页
        # 保持登录状态
        login(request, user)

        # 设置首页用户名
        response = redirect(reverse('contents:index'))
        response.set_cookie('username', user.username, max_age=24 * 14 * 3600)
        # 重定向 首页

        return response

class QQAuthURLView(View):
    def get(self, request):
        """
    QQ_CLIENT_ID = '101518219'
    QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
    QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'
           uri>url
        :param request:
        :return:
        """

        # 1.返回QQ登录地址---和QQ平台认证通过 实例化认证对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        # 2.获取qq_login_url
        login_url = oauth.get_qq_url()

        # 3.返回给前端
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})
