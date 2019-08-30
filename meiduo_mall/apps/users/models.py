from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # 系统自带 username password(加解密)
    # 增加自己的字段 mobile 手机号
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    class Meta:
        db_table = "tb_users"
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
