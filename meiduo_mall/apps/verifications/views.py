from django.shortcuts import render
from django.views import View
from django import http

from apps.verifications import contants

# 2.短信验证码
from utils.response_code import RETCODE


class SmsCodeView(View):
    def get(self, request, mobile):
        # *  1.接收 2个 mobile; 图片验证码img_code
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # *  2.验证码 img_code和redis存储的验证码 是否一致 (1.redis取出来(4步) 2.判断是否相等 3.redis img_code 删除) **千万注意 redis取出来类型 是 Bytes.decode()**
        from django_redis import get_redis_connection
        img_client = get_redis_connection('verify_image_code')
        img_code_redis = img_client.get('img_%s' % uuid)

        if img_code_redis is None:
            return http.JsonResponse({'code': "4001", 'errmsg': '图形验证码失效了'})

        # 删除图片验证码
        img_client.delete('img_%s' % uuid)

        # 判断是否相等 千万注意 redis返回的是bytes类型
        if img_code_redis.decode().lower() != image_code.lower():
            return http.JsonResponse({'code': "4001", 'errmsg': '输入图形验证码有误'})

        # *   3.生成随机 6位 短信验证码内容 random.randit()
        from random import randint
        sms_code = '%06d' % randint(0, 999999)
        # *   4.存储 随机6位 redis里面(3步 )
        sms_client = get_redis_connection('sms_code')

        # 1.获取 频繁发送短信的 标识
        send_flag = sms_client.get('send_flag_%s' % mobile)

        # 2.判断标识 是否存在
        if send_flag:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁66'})

        # 3.标识不存在 ,重新倒计时
        p1 = sms_client.pipeline()
        p1.setex('send_flag_%s' % mobile, 60, 1)
        p1.setex('sms_%s' % mobile, contants.SMS_CODE_REDIS_EXPIRE, sms_code)
        p1.execute()
        # *   5.发短信---第三方容联云--
        # from libs.yuntongxun.sms import CCP
        # CCP().send_template_sms('手机号', ['验证码', 过期时间], 短信模板1)
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        print(sms_code)

        # *   6.返回响应对象
        return http.JsonResponse({'code': '0', 'errmsg': '发送短信成功'})


# 4. 图片验证码 image_codes/(?P<uuid>[\w-]+)/
class ImageCodeView(View):
    def get(self, request, uuid):
        # 2.校验uuid正则
        # 3.生成图片验证码
        from libs.captcha.captcha import captcha
        text, image = captcha.generate_captcha()

        # 4. 验证码的数字 存储到 redis
        # 4.1 导包
        from django_redis import get_redis_connection
        # 4.2 链接数据库
        img_client = get_redis_connection('verify_image_code')
        # 4.3 存储
        img_client.setex('img_%s' % uuid, contants.IMAGE_CODE_REDIS_EXPIRE, text)

        # 5. 给前端返回 图片验证码 bytes
        return http.HttpResponse(image, content_type='image/jpeg')
