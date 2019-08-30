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

