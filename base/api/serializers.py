import base64
from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator

from votings import settings
from ..models import *

UserModel = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'

    def create(self, validated_data: dict) -> UserModel:
        user = UserModel.objects.create_user(email=validated_data['email'], username=validated_data['username'],
                                             password=validated_data['password'])
        user.save()
        return user


class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'

    def create(self, validated_data: dict) -> Poll:
        choices = self.initial_data['choices']
        if len(choices) == len(set(choices)):
            poll = Poll.objects.create(**validated_data)
            for choice in choices:
                poll.choice_set.create(choice=choice)
            poll.save()
            return poll
        else:
            raise serializers.ValidationError('Choices must be unique')

    def update(self, instance: Poll, validated_data: dict) -> Poll:
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


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


def send_password_reset_email(email: str) -> None:
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return

    uidb64 = base64.urlsafe_b64encode(str(user.pk).encode()).decode()
    token = default_token_generator.make_token(user)
    reset_url = f'http://localhost:3000/password_reset/{uidb64}/{token}'

    subject = 'Сброс пароля'
    message = f'Здравствуйте, для сброса пароля перейдите по ссылке {reset_url}'
    recipient_list = [email]
    send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email: str) -> str:
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Пользователь с таким email не существует.")
        return email

    def send_email(self) -> None:
        email = self.validated_data['email']
        send_password_reset_email(email)


class CheckPasswordTokenSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs: dict) -> bool:
        attrs = super().validate(attrs)
        uidb64 = attrs['uidb64']
        token = attrs['token']

        try:
            uid = base64.urlsafe_b64decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (ValueError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            return True
        raise serializers.ValidationError('Некорректные данные или токен сброса пароля не существует.')
