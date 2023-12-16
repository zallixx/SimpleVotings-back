from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from base.api.serializers import RegisterSerializer, PollSerializer, ComplainSerializer
from base.api.validations import custom_validation
from ..models import Poll, Vote, User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token',
        '/api/token/refresh',
    ]
    return Response(routes)


@api_view(['POST'])
def register(request):
    clean_data = custom_validation(request.data)
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = serializer.create(clean_data)
        if user:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_poll(request):
    request.data.update({'created_by': request.user.user_id})
    serializer = PollSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_polls(request):
    polls = Poll.objects.all()
    serializer = PollSerializer(polls, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_poll(request, pk):
    poll = Poll.objects.get(id=pk)
    serializer = PollSerializer(poll, many=False)
    choices = []
    for choice in poll.choice_set.all():
        choices.append(str(choice))
    to_return = dict(serializer.data)
    to_return.update({'choices': choices})
    return Response(to_return)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_poll(request, pk):
    poll = Poll.objects.get(id=pk)
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
def vote(request, pk):
    poll = Poll.objects.get(id=pk)
    try:
        choices = request.data['choices']
        if len(Vote.objects.filter(user=request.user, poll=poll)) > 0:
            return Response('You have already voted', status=status.HTTP_400_BAD_REQUEST)
        if poll.type_voting == 1:
            for choice in choices:
                poll.choice_set.get(choice=choice).add_vote()
                vote_field = Vote(poll=poll, user=request.user)
                vote_field.save()
                poll.save()
            return Response('Voted', status=status.HTTP_201_CREATED)
        elif len(choices) > 1:
            return Response('You are not allowed to select more than one choice', status=status.HTTP_400_BAD_REQUEST)
        else:
            poll.choice_set.get(choice=choices[0]).add_vote()
            vote_field = Vote(poll=poll, user=request.user)
            vote_field.save()
            poll.save()
            return Response('Voted', status=status.HTTP_201_CREATED)
    except:
        return Response('You need to select at least one choice', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complain(request, pk):
    poll = Poll.objects.get(id=pk)
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
def results(request, pk):
    if Vote.objects.filter(user=request.user, poll=pk).exists():
        poll = Poll.objects.get(id=pk)
        serializer = PollSerializer(poll, many=False)
        choices = []
        for choice in poll.choice_set.all():
            choices.append([str(choice), choice.votes])
        to_return = dict(serializer.data)
        to_return.update({'choices': choices})
        return Response(to_return, status=status.HTTP_200_OK)
    return Response('You have not voted yet', status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_author_name(request, pk):
    if User.objects.filter(user_id=pk).exists():
        user = User.objects.get(user_id=pk)
        return Response(user.username, status=status.HTTP_200_OK)
    return Response('User does not exist', status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_poll(request, pk):
    poll = Poll.objects.get(id=pk)
    if poll.created_by.user_id == request.user.user_id:
        poll.delete()
        return Response('Deleted', status=status.HTTP_200_OK)
    return Response('You cannot delete this poll', status=status.HTTP_400_BAD_REQUEST)
