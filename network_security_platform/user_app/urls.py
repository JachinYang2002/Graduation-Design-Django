from django.urls import re_path
from rest_framework_jwt.views import obtain_jwt_token
from user_app import views

urlpatterns = [
    re_path('^login/$', views.UserLoginAPIView.as_view(), name='login'),
    re_path('^register/$', views.UserRegisterAPIView.as_view(), name='register'),
    re_path('^logout/$', views.UserLogoutAPIView.as_view(), name='logout'),
    re_path('^register/send_sms_code/$', views.SMSCodeAPIView, name="send_sms_code"),
    re_path('^homepage/edit_username/$', views.EditUsernameAPIView, name="edit_username"),
]
