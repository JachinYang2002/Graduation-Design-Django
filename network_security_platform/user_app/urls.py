from django.urls import re_path

from user_app import views

urlpatterns = [
    re_path('^login_register/$', views.UserLoginRegisterAPIView, name='login_register'),
    re_path('^logout/$', views.UserLogoutAPIView, name='logout'),
]
