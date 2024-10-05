from rest_framework import serializers
from CTF_app.models import WebChallenge


class UploadWebChallengeSerializer(serializers.ModelSerializer):
    """
    上传web题的序列化类
    """
    class Meta:
        model = WebChallenge
        fields = ['title', 'description', 'ip', 'points', 'exp', 'flag', 'question_type']

    def validate(self, attrs):
        if not all(attrs.get(field) for field in ['title', 'description', 'ip', 'points', 'exp', 'flag', 'question_type']):
            raise serializers.ValidationError('缺少必要参数')
        return attrs
