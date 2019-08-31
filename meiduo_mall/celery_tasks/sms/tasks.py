# !/usr/bin/env python
# _*_ coding:utf-8 _*_
from celery_tasks.main import app


@app.task
def ccp_send_sms_code(mobile, sms_code):
    from libs.yuntongxun.sms import CCP
    result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    print(sms_code)

    return result
