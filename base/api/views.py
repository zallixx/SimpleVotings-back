import base64
from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.views import TokenObtainPairView

from base.api.serializers import RegisterSerializer, PollSerializer, ComplainSerializer, VoteSerializer, UserSerializer, \
    ResetPasswordSerializer, CheckPasswordTokenSerializer
from base.api.validations import custom_validation
from ..models import Poll, Vote, User, Complain


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User) -> Token:
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        token['is_admin'] = user.is_admin
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
def getRoutes(request: Request) -> Response:
    routes = [
        '/api/token',
        '/api/token/refresh',
    ]
    return Response(routes)


@api_view(['POST'])
def register(request: Request) -> Response:
    clean_data = custom_validation(request.data)
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.create(clean_data)
        if user:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_poll(request: Request) -> Response:
    request.data.update({'created_by': request.user.user_id})
    serializer = PollSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_polls(request: Request) -> Response:
    polls = Poll.objects.all()
    serializer = PollSerializer(polls, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_poll(request: Request, pk: int) -> Response:
    try:
        poll = Poll.objects.get(id=pk)
    except Poll.DoesNotExist:
        return Response("Poll does not exist", status=status.HTTP_404_NOT_FOUND)
    serializer = PollSerializer(poll, many=False)
    choices = []
    for choice in poll.choice_set.all():
        choices.append(str(choice))
    to_return = dict(serializer.data)
    to_return.update({'choices': choices})
    return Response(to_return)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_poll(request: Request, pk: int) -> Response:
    try:
        poll = Poll.objects.get(id=pk)
    except Poll.DoesNotExist:
        return Response("Poll does not exist", status=status.HTTP_404_NOT_FOUND)
    serializer = PollSerializer(poll, data=request.data, partial=True)
    if ('created_by' in request.data.keys() and request.data['created_by'] == request.user.user_id) or (
            poll.created_by.user_id == request.user.user_id):
        if serializer.is_valid():
            serializer.save()
            choices = []
            for choice in poll.choice_set.all():
                choices.append(str(choice))
            to_return = dict(serializer.data)
            to_return.update({'choices': choices})
            return Response(to_return)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vote(request: Request, pk: int) -> Response:
    try:
        poll = Poll.objects.get(id=pk)
    except Poll.DoesNotExist:
        return Response("Poll does not exist", status=status.HTTP_404_NOT_FOUND)
    try:
        choices = request.data['choices']
        print(choices)
        if len(Vote.objects.filter(user=request.user, poll=poll)) > 0:
            return Response('You have already voted', status=status.HTTP_400_BAD_REQUEST)
        if poll.special == 1:
            if poll.participants_amount_voted >= poll.amount_participants:
                return Response('Poll is closed', status=status.HTTP_400_BAD_REQUEST)
        if poll.special == 2:
            print(datetime.now())
            print(datetime.strptime(poll.remaining_time, '%a, %d %b %Y %H:%M:%S GMT') + timedelta(hours=3))
            if datetime.now() < datetime.strptime(poll.remaining_time, '%a, %d %b %Y %H:%M:%S GMT'):
                return Response('Poll is closed', status=status.HTTP_400_BAD_REQUEST)
        if poll.type_voting == 1:
            for choice in choices:
                poll.choice_set.get(choice=choice).add_vote()
                poll.choice_set.get(choice=choice).add_participant(user=request.user)
                poll.participants_amount_voted += 1
                poll.save()
            vote_field = Vote(poll=poll, user=request.user)
            vote_field.save()
            return Response('Voted', status=status.HTTP_201_CREATED)
        elif len(choices) > 1:
            return Response('You are not allowed to select more than one choice', status=status.HTTP_400_BAD_REQUEST)
        else:
            poll.choice_set.get(choice=choices[0]).add_vote()
            poll.choice_set.get(choice=choices[0]).add_participant(user=request.user)
            vote_field = Vote(poll=poll, user=request.user)
            vote_field.save()
            poll.participants_amount_voted += 1
            poll.save()
            return Response('Voted', status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        return Response('You need to select at least one choice', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complain(request: Request, pk: int) -> Response:
    try:
        poll = Poll.objects.get(id=pk)
    except Poll.DoesNotExist:
        return Response("Poll does not exist", status=status.HTTP_404_NOT_FOUND)
    if poll.created_by.user_id == request.user.user_id:
        return Response('You cannot complain about your own poll', status=status.HTTP_400_BAD_REQUEST)
    complaint = ComplainSerializer(data=(request.data | {'user': request.user.user_id, 'poll': poll.id}))
    print(complaint)
    if complaint.is_valid():
        complaint.save()
        return Response('Complained', status=status.HTTP_201_CREATED)
    return Response(complaint.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_complains(request: Request) -> Response:
    complains = Complain.objects.filter(user_id=request.user.user_id)
    serializer = ComplainSerializer(complains, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_complains_unread(request: Request) -> Response:
    complains = Complain.objects.filter(status='Отправлена. Ожидает рассмотрения.')
    serializer = ComplainSerializer(complains, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_answer_complain(request: Request, pk: int) -> Response:
    if not Complain.objects.filter(id=pk).exists():
        return Response("Complain does not exist", status=status.HTTP_404_NOT_FOUND)
    if request.user.is_admin:
        complains = Complain.objects.filter(id=pk)
        complains.update(status='Рассмотрена', response=request.data['response'])
        return Response("Ответ отправлен", status=status.HTTP_200_OK)
    return Response("Недостаточно прав", status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_complain(request: Request, pk: int) -> Response:
    complains = Complain.objects.filter(id=pk)
    serializer = ComplainSerializer(complains, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def results(request: Request, pk: int) -> Response:
    if Vote.objects.filter(user=request.user, poll=pk).exists():
        try:
            poll = Poll.objects.get(id=pk)
        except Poll.DoesNotExist:
            return Response("Poll does not exist", status=status.HTTP_404_NOT_FOUND)
        serializer = PollSerializer(poll, many=False)
        choices = []
        for choice in poll.choice_set.all():
            choices.append([str(choice), choice.votes, choice.participants_array])
        to_return = dict(serializer.data)
        to_return.update({'choices': choices})
        return Response(to_return, status=status.HTTP_200_OK)
    return Response('You have not voted yet', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_author_name(request: Request, pk: int) -> Response:
    if User.objects.filter(user_id=pk).exists():
        user = User.objects.get(user_id=pk)
        return Response(user.username, status=status.HTTP_200_OK)
    return Response('User does not exist', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vote_history(request: Request) -> Response:
    anotherUser = request.GET.get('anotherUser')
    if anotherUser:
        votes = Vote.objects.filter(user_id=anotherUser)
    else:
        votes = Vote.objects.filter(user_id=request.user.user_id)
    serializer = VoteSerializer(votes, many=True)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_poll(request: Request, pk: int) -> Response:
    try:
        poll = Poll.objects.get(id=pk)
    except Poll.DoesNotExist:
        return Response("Poll does not exist", status=status.HTTP_404_NOT_FOUND)
    if poll.created_by.user_id == request.user.user_id:
        poll.delete()
        return Response('Deleted', status=status.HTTP_200_OK)
    return Response('You cannot delete this poll', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request: Request) -> Response:
    user = User.objects.get(user_id=request.user.user_id)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request: Request) -> Response:
    user = User.objects.get(user_id=request.user.user_id)
    if user.check_password(request.data['old_password']):
        user.set_password(request.data['new_password'])
        user.save()
        return Response('Password changed', status=status.HTTP_200_OK)
    return Response('Wrong password', status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_user_data(request: Request) -> Response:
    user = User.objects.get(user_id=request.user.user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request: Request, pk: int) -> Response:
    if User.objects.filter(user_id=pk).exists():
        user = User.objects.get(user_id=pk)
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response('User does not exist', status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request: Request) -> Response:
    user = User.objects.get(user_id=request.user.user_id)
    user.delete()
    return Response('Deleted', status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password(request: Request) -> Response:
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.send_email()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_password_tokens(request: Request, uidb64: str, token: str) -> Response:
    serializer = CheckPasswordTokenSerializer(data={'uidb64': uidb64, 'token': token})
    if serializer.is_valid(raise_exception=True):
        if serializer.validate({'uidb64': uidb64, 'token': token}):
            user = User.objects.get(pk=base64.urlsafe_b64decode(uidb64).decode())
            user.set_password(request.data['password'])
            user.save()
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
