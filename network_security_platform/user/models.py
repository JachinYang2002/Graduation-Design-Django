from django.db import models
from utils import base_model


# Create your models here.
class UserBaseInfoModel(base_model.BaseModel):
    """
    用户基本信息模型
    """
    SEX_CHOICE = (
        (0, "secret"),
        (1, "man"),
        (2, 'female')
    )
    
    user_name = models.CharField(verbose_name='昵称', max_length=10, unique=True)
    user_pwd = models.CharField(verbose_name='密码', max_length=200)
    tel_number = models.CharField(verbose_name='注册手机号' ,max_length=11, unique=True)
    gender = models.IntegerField(verbose_name='性别' ,choices=SEX_CHOICE, default=0)
    user_id = models.CharField(verbose_name='用户唯一标识ID', max_length=20)
    signature = models.TextField(verbose_name='个性签名', null=True, blank=True)
    # avatar = models.ImageField(verbose_name='头像' ,upload_to='', null=True, blank=True)

    class Meta:
        db_table = 't_user_base_info'
        verbose_name = "用户基本信息"
        verbose_name_plural = verbose_name

