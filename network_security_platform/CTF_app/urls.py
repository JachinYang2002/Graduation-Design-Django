from django.urls import path, include, re_path
from CTF_app import views

urlpatterns = [
    re_path('^topic/$', views.CTFTopicView.as_view(), name='nginx'),
]
