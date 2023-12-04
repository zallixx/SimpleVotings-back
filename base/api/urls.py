from django.urls import path
from . import views
from .views import MyTokenObtainPairView, create_poll, PollDetailView, PollEdit

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegisterView.as_view()),
    path('polls/new', create_poll, name='create_poll'),
    path('polls/', views.get_polls, name='view_polls'),
    path('polls/<int:pk>/', PollDetailView.as_view(), name='poll-detail'),
    path('polls/<int:pk>/edit/', PollEdit.as_view(), name='poll-edit'),
    path('', views.getRoutes),
]