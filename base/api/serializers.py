from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models import Poll

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
        model = Poll
        fields = '__all__'

    def create(self, validated_data):
        poll = Poll.objects.create(**validated_data)
        for choice in self.initial_data['choices']:
            poll.choice_set.create(choice=choice)
        poll.save()
        return poll
