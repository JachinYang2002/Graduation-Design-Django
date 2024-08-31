from django.urls import re_path

from user import views

urlpatterns = [
    re_path('^login_register/$', views.UserLoginAPIView.as_view()),
]
