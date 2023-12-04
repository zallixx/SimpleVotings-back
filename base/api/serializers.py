from django.contrib.auth import get_user_model
from rest_framework import serializers
from ..models import Poll_model

UserModel = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'

    def create(self, validated_data):
        user = UserModel.objects.create_user(email=validated_data['email'], username=validated_data['username'],
                                             password=validated_data['password'])
        user.save()
        return user


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll_model
        fields = '__all__'
