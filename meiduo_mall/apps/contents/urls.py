from django.conf.urls import url, include

from . import views

urlpatterns = [
        # contents
        url(r'^$', views.IndexView.as_view(), name='index'),

]
