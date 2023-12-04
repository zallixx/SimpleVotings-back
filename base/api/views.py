import datetime

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from base.api.serializers import RegisterSerializer, PollSerializer
from base.api.validations import custom_validation
from ..models import Poll_model


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


class UserRegisterView(APIView):
    def post(self, request):
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
    request.data.update({'created_by': request.user})
    serializer = PollSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PollDetailView(generics.ListAPIView):
    queryset = Poll_model.objects.all()
    serializer_class = PollSerializer


class PollEdit(generics.RetrieveUpdateDestroyAPIView):
    queryset = Poll_model.objects.all()
    serializer_class = PollSerializer

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.redacted_at = datetime.datetime.now()
        instance.save()
        instance.question = request.data.get(instance.question)
        instance.answers = request.data.get(instance.answers)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
