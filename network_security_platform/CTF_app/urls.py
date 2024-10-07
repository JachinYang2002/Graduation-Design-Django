from django.urls import path, include, re_path
from CTF_app import views

urlpatterns = [
    re_path('^web_topic/$', views.CTFWebTopicView.as_view(), name='web_topic'),
    re_path('^check_web_flag/$', views.CTFWebCheckFlagView.as_view(), name='check_web_flag'),
    re_path('^fetch_web_info/$', views.CTFWebListView.as_view(), name='fetch_web_info'),
    re_path('^upload_web/$', views.UploadWebChallengeView.as_view(), name='upload_web'),
]
