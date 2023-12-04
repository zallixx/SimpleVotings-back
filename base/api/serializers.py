from django.contrib.auth import get_user_model
from rest_framework import serializers

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
