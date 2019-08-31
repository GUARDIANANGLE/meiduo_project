from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^qq/login/$', views.QQAuthURLView.as_view()),

    # 接收 QQ 返回来的 code  /oauth_callback
    url(r'^oauth_callback/$', views.QQAuthView.as_view()),


]
