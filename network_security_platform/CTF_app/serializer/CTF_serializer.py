from rest_framework import serializers
from CTF_app.models import WebChallenge, UserWebQuestionStatus


class UploadWebChallengeSerializer(serializers.ModelSerializer):
    """
    上传web题的序列化类
    """
    class Meta:
        model = WebChallenge
        fields = ['title', 'description', 'points', 'exp', 'flag', 'question_type', 'level']

    def validate(self, attrs):
        if not all(attrs.get(field) for field in ['title', 'description', 'points', 'exp', 'flag', 'question_type']):
            raise serializers.ValidationError('缺少必要参数')
        return attrs

# ============================================== Web ========================================================
class CTFWebStatusSerializer(serializers.ModelSerializer):
    """
    获取用户每一 Web 题的状态
    """
    class Meta:
        model = UserWebQuestionStatus
        fields = ['is_completed']


class CTFWebListSerializer(serializers.ModelSerializer):
    """
    发送Web题的数据到前端
    """
    status = CTFWebStatusSerializer(read_only=True)
    class Meta:
        model = WebChallenge
        fields = ['title', 'description', 'points', 'exp', 'status', 'level']


