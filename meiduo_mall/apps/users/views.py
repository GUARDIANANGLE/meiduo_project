import json

from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
import re
from django import http

from apps.areas.models import Address
from meiduo_mall.settings.dev import logger
from apps.users.models import User

from django.contrib.auth.mixins import LoginRequiredMixin
from utils.response_code import RETCODE


# 修改地址
class UpdateAddressView(View):
    def put(self, request, address_id):
        # 1.接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 2.正则校验

        # 3. 修改数据
        Address.objects.filter(id=address_id).update(
            user=request.user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email
        )

        # 4. 返回前端  字典dict 进行局部更新
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '更新地址成功', 'address': address_dict})


    def delete(self,request,address_id):

        # 1.接收解析参数 address_id

        # 2.修改 is_deleted=True
        address = Address.objects.get(id=address_id)
        address.is_deleted = True
        address.save()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除地址成功'})

# 11.默认地址
class DefaultAddressView(LoginRequiredMixin, View):
    def put(self, request, address_id):
        # 1. 接收参数

        # 2.查询 当前的地址
        address = Address.objects.get(id=address_id)
        # 3. 修改user的 defalut_address
        request.user.defalut_address = address
        request.user.save()

        # 4. 返回响应对象
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '设置默认地址成功'})


# 10.增加收货地址
class CreateAddressView(LoginRequiredMixin, View):
    def post(self, request):

        # 判断 收货地址的个数 大于20 ; return
        count = Address.objects.filter(user=request.user, is_deleted=False).count()
        # count = request.user.addresses.count()
        if count > 20:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        # 1.接收参数  json
        json_dict = json.loads(request.body.decode())
        receiver = json_dict['receiver']
        province_id = json_dict['province_id']
        city_id = json_dict['city_id']
        district_id = json_dict['district_id']
        place = json_dict['place']
        mobile = json_dict['mobile']
        tel = json_dict['tel']
        email = json_dict['email']

        # 2.正则校验

        # 3.create
        address = Address.objects.create(
            user=request.user,
            title=receiver,
            receiver=receiver,
            province_id=province_id,
            city_id=city_id,
            district_id=district_id,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email
        )

        # 设置默认地址:
        default_address = request.user.default_address
        if not default_address:
            request.user.default_address = address
            request.user.save()

        # 4.构建前端 dict
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 5.返回
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


# 9.收货地址
class AddressView(LoginRequiredMixin, View):
    def get(self, request):
        # 1.查询当前用户的  所有地址
        user = request.user
        addresses = Address.objects.filter(user=user, is_deleted=False)

        # 2. 构建前端需要的数据格式
        address_dict_list = []
        for address in addresses:
            add_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(add_dict)

        context = {
            'default_address_id': user.default_address_id,
            'addresses': address_dict_list,
        }

        return render(request, 'user_center_site.html', context)


def check_verify_email_token(token):
    # 解密
    from utils.secret import SecretOauth
    json_dict = SecretOauth().loads(token)

    try:
        user = User.objects.get(id=json_dict['user_id'], email=json_dict['email'])
    except Exception as e:
        logger.error(e)
        return None
    else:
        return user


class VerifyEmailView(LoginRequiredMixin, View):
    def get(self, request):
        # 1.接收参数
        json_str = request.GET.get('token')

        # .校验 用户是否存在 同时 邮箱也是对的
        user = check_verify_email_token(json_str)

        if not user:
            return http.HttpResponseForbidden('无效的token')

        # 2. 修改 对象的 email_active 字段
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('激活邮箱失败了!')

        # 3.返回响应结果
        return redirect(reverse('users:info'))


# 7.邮箱 添加
class EmailView(LoginRequiredMixin, View):
    def put(self, request):
        # 1.接收 请求体非表单参数 json
        json_bytes = request.body
        json_str = json_bytes.decode()
        json_dict = json.loads(json_str)
        email = json_dict.get('email')

        # 2.正则校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        # 3. 修改 数据库中 email值
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)

            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        # 自动发邮件 email
        token_value = {
            'user_id': request.user.id,
            'email': email
        }
        from utils.secret import SecretOauth
        secret_str = SecretOauth().dumps(token_value)
        verify_url = settings.EMAIL_ACTIVE_URL + "?token=" + secret_str
        from celery_tasks.email.tasks import send_verify_email
        send_verify_email.delay(email, verify_url)

        # 4. 返回前端结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


# 6.个人中心--隐私信息LoginRequiredMixin
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        # request.user.username
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request, 'user_center_info.html', context)


# 5.退出登录
class LogOutView(View):
    def get(self, request):
        # 1,.退出的本质 (删除session)
        from django.contrib.auth import logout
        logout(request)

        # 2.清空cookie --首页的用户名
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        return response


# 4.登录
class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    # 2.登录功能
    def post(self, request):
        # 1.接收三个参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')

        # 2.校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden('参数不齐全')
        # 2.1 用户名
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # 2.2 密码
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        # *   4. 数据交互 username,password  django自带的认证函数 authenticate()
        from django.contrib.auth import authenticate, login
        user = authenticate(username=username, password=password)

        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})

        # *   5. 保持登录状态
        login(request, user)

        # *   6. 记住登录
        if remembered == "on":
            # 记住的--设置过期时间 2周
            request.session.set_expiry(None)
        else:
            # 没记住--会话结束 就过期
            request.session.set_expiry(0)

        # *   7. 跳转首页 index
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('contents:index'))

        response.set_cookie('username', username, max_age=24 * 14 * 3600)
        return response


# 3. 手机号是否重复 mobiles/(?P<mobile>1[3-9]\d{9})/count/
class MobileCountView(View):
    def get(self, request, mobile):
        # 2.正则校验
        # 3.查询数据mobile字段 返回个数
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': '0', 'errmsg': "OK", "count": count})


# 2.判断用户名是否重复
class UsernameCountView(View):
    def get(self, reqeust, username):
        # 2.校验正则
        # 3. 查询数据库的用户名
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': '0', 'errmsg': "OK", "count": count})


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
        # if not all([username, password, password2, mobile, allow]):
        #     return http.HttpResponseForbidden('缺少参数!')
        # # *   1.用户名: ---------判空,正则校验,是否重复
        # if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
        #     return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # # *   2.密码:   --------- 判空,正则校验
        # if not re.match('^^[0-9A-Za-z]{8,20}$', password):
        #     return http.HttpResponseForbidden('请输入8-20位的密码')
        # # *   3.确认密码: ---------判空,判断是否相等
        # if password2 != password:
        #     return http.HttpResponseForbidden('两次密码输入不一致')
        # # *   4.手机号:---------   判空,正则校验,是否重复
        # if not re.match('^1[345789]\d{9}$', mobile):
        #     return http.HttpResponseForbidden('请输入正确的手机号码')
        #
        # # *   5.图形验证码:
        # # *   6.短信验证码:
        # sms_code = request.POST.get('msg_code')
        #
        # from django_redis import get_redis_connection
        # sms_client = get_redis_connection('sms_code')
        # sms_code_redis = sms_client.get('sms_%s' % mobile)
        #
        # if sms_code_redis is None:
        #     return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        # # 删除sms_coderedis
        # sms_client.delete('sms_%s' % mobile)
        #
        # if sms_code != sms_code_redis.decode():
        #     return render(request, 'register.html', {'sms_code_errmsg': '短信验证码有误!'})
        #
        #
        # # *   7.同意”美多商城用户使用协议“: 判断是否选中
        # if allow != 'on':
        #     return http.HttpResponseForbidden('请求协议!')

        # 3. 注册用户
        try:
            from apps.users.models import User
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except Exception as e:
            logger.error(e)
            return render(request, 'register.html')

        # 4.保持登录状态: cookie ---session
        from django.contrib.auth import login
        login(request, user)

        # 5. 重定向到首页

        response = redirect(reverse('contents:index'))
        # 注册时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

        return response

class ChangePasswordView(LoginRequiredMixin, View):
    """修改密码"""

    def get(self, request):
        """展示修改密码界面"""
        return render(request, 'user_center_pass.html')

    def post(self, request):
        """实现修改密码逻辑"""
        # 接收参数
        old_password = request.POST.get('old_pwd')
        new_password = request.POST.get('new_pwd')
        new_password2 = request.POST.get('new_cpwd')

        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 校验密码是否正确
        result = request.user.check_password(old_password)
        # result 为false 密码不正确
        if not result:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg':'原始密码错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')
        if new_password != new_password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')

        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_pwd_errmsg': '修改密码失败'})

        # 清理状态保持信息
        logout(request)
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        # # 响应密码修改结果：重定向到登录界面
        return response