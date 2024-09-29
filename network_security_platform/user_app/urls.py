from django.urls import re_path
from user_app import views

urlpatterns = [
    re_path('^login/$', views.UserLoginAPIView.as_view(), name='login'),
    re_path('^register/$', views.UserRegisterAPIView.as_view(), name='register'),
    re_path('^logout/$', views.UserLogoutAPIView.as_view(), name='logout'),
    re_path('^register/send_sms_code/$', views.SMSCodeAPIView.as_view(), name="send_sms_code"),
    re_path('^fetch_userinfo/$', views.FetchUserInfoAPIView.as_view(), name="fetch_userinfo"),
    re_path('^homepage/edit_username/$', views.EditUsernameAPIView.as_view(), name="edit_username"),
]
