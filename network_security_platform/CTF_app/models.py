from django.db import models


class BaseChallenge(models.Model):
    """
    CTF 题的基类
    """
    title = models.CharField(verbose_name='题目名称', max_length=255)
    description = models.TextField(verbose_name='题目描述')
    points = models.IntegerField(verbose_name='奖励点', default=30)
    exp = models.IntegerField(verbose_name='奖励经验', default=10)
    flag = models.CharField(verbose_name='题目答案flag', max_length=100)
    level = models.IntegerField(verbose_name='题目难度等级', default=0)  # 0：初级  1：中级 2：高级

    class Meta:
        abstract = True  # 使这个类成为一个抽象基类

    def __str__(self):
        return self.title


# 题库模型
class CTFQuestionType(models.Model):
    title = models.CharField(max_length=200, verbose_name="题库类型")

    class Meta:
        db_table = 't_CTF_question_type'
        verbose_name = "题库类型表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class WebChallenge(BaseChallenge):
    # Web 特定的字段
    question_type = models.ForeignKey("CTFQuestionType", on_delete=models.SET_NULL, verbose_name="所属题目类型", related_name='web_list',null=True, blank=True)

    class Meta:
        db_table = 't_CTF_web_info'
        verbose_name = 'Web题型的信息表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class CryptoChallenge(BaseChallenge):
    # Crypto 特定的字段
    class Meta:
        db_table = 't_CTF_crypto_info'
        verbose_name = 'Crypto题型的信息表'
        verbose_name_plural = verbose_name

class PwnChallenge(BaseChallenge):
    # Pwn 特定的字段
    class Meta:
        db_table = 't_CTF_pwn_info'
        verbose_name = 'Pwn题型的信息表'
        verbose_name_plural = verbose_name

class MiscChallenge(BaseChallenge):
    # Misc 特定的字段
    class Meta:
        db_table = 't_CTF_misc_info'
        verbose_name = 'Misc题型的信息表'
        verbose_name_plural = verbose_name


class UserWebQuestionStatus(models.Model):
    """
    用户Web解题状态模型
    """
    user_tag = models.ForeignKey('user_app.UserBaseInfoModel', verbose_name='用户', on_delete=models.SET_NULL, related_name='user_topic', null=True, blank=True)
    web_question = models.ForeignKey("WebChallenge", verbose_name='web题', on_delete=models.CASCADE, related_name='web_topic')
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")


    class Meta:
        unique_together = ('user_tag', 'web_question')  # 确保每个用户对每个题目只有一条记录
        db_table = 't_CTF_user_web_status'
        verbose_name = '用户Web题型解题状态表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user_tag} - {self.web_question}'


class WebActiveChallenge(models.Model):
    """
    已开启的Web题镜像
    """
    image = models.ForeignKey('WebChallenge', verbose_name='容器对应的镜像', on_delete=models.CASCADE, related_name='web_active_question')
    user_tag = models.ForeignKey('user_app.UserBaseInfoModel', verbose_name='开启容器的用户', on_delete=models.CASCADE, related_name='web_active_topic')
    question_name = models.CharField(verbose_name='容器名称', max_length=50)
    port = models.IntegerField(verbose_name='分配出的端口号')

    class Meta:
        db_table = 't_CTF_web_active'
        verbose_name = 'Web题型分配出的端口号表'
        verbose_name_plural = verbose_name

