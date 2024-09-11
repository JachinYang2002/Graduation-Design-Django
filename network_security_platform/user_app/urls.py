from django.urls import re_path

from user_app import views

urlpatterns = [
    re_path('^login_register/$', views.UserLoginAPIView.as_view(), name='login_register'),
    re_path('^logout/$', views.UserLogoutAPIView.as_view(), name='logout'),
]
