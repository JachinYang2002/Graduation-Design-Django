from django.urls import path, include, re_path
from CTF_app import views

urlpatterns = [
    re_path('^web_topic/$', views.CTFWebTopicView.as_view(), name='web_topic'),
    re_path('^upload_web/$', views.UploadWebChallengeView.as_view(), name='upload_web'),
]
