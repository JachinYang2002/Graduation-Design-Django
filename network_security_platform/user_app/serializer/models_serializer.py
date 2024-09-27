from rest_framework.serializers import ModelSerializer
from user_app.models import UserBaseInfoModel


class UserBaseInfoModelSerializer(ModelSerializer):
    class Meta:
        model = UserBaseInfoModel
        fields = '__all__'
