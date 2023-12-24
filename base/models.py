from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields import ArrayField
from django.db import models


class UserManager(BaseUserManager):
    """Manager for User model"""

    def create_user(self, username, email, password):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have a username')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """Model of user"""
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(max_length=60, unique=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    age = models.IntegerField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    show_history = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    quote = models.TextField(null=True, blank=True)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    USER_ID_FIELD = 'user_id'

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class PollType(models.IntegerChoices):
    SINGLE = 0
    MULTIPLE = 1
    DISCRETE = 2


class Poll(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    redacted_at = models.DateTimeField(auto_now=True, blank=True)
    type_voting = models.IntegerField(choices=PollType.choices, default=PollType.DISCRETE,
                                      verbose_name='Тип голосования')
    author_name = models.CharField(max_length=255)
    special = models.IntegerField(default=0)
    remaining_time = models.DateTimeField(auto_now_add=True, blank=True)
    amount_participants = models.IntegerField(default=-1, blank=True)
    participants_amount_voted = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.question


class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.CharField(max_length=255)
    votes = models.IntegerField(default=0)
    participants_array = models.JSONField(default=list)

    def add_vote(self):
        self.votes += 1
        self.save()

    def add_participant(self, user):
        self.participants_array.append(user.user_id)
        self.save()

    def __str__(self):
        return self.choice

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

class Complain(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.TextField()
    status = models.TextField(default='Отправлена. Ожидает рассмотрения.')
    response = models.TextField(default='')
