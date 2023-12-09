from django.contrib.auth import get_user_model
from django.utils.datetime_safe import datetime
from rest_framework import serializers

from ..models import Poll, Complain

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

    def update(self, instance, validated_data):
        if 'question' in validated_data:
            instance.question = validated_data.get('question')
        if 'type_voting' in validated_data:
            instance.type_voting = validated_data.get('type_voting')
        if 'choices' in self.initial_data:
            instance.choice_set.all().delete()
            for choice in self.initial_data.get('choices'):
                instance.choice_set.create(choice=choice)
        instance.redacted_at = datetime.now()
        instance.save()
        return instance


class ComplainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complain
        fields = '__all__'
