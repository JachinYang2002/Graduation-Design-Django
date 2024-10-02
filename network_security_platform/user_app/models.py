from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms
from utils import base_model


# Create your models here.
class UserBaseInfoModel(AbstractUser ,base_model.BaseModel):
    """
    用户基本信息模型
    """
    
    username = models.CharField(verbose_name='昵称', max_length=10, unique=True)
    password = models.CharField(verbose_name='密码', max_length=128)
    telephone = models.CharField(verbose_name='注册手机号' ,max_length=11, unique=True)
    email = models.CharField(verbose_name='用户邮箱', max_length=255, unique=True)
    gender = models.CharField(verbose_name='性别' , default='0', max_length=1)
    user_id = models.CharField(verbose_name='用户唯一标识ID', max_length=20)
    signature = models.TextField(verbose_name='个性签名', null=True, blank=True)
    avatar = models.ImageField(verbose_name='头像' ,upload_to='user_avatar/%Y/%m/%d/', null=True, blank=True)

    class Meta:
        db_table = 't_user_base_info'
        verbose_name = "用户基本信息"
        verbose_name_plural = verbose_name



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserBaseInfoModel
        fields = ['avatar']

