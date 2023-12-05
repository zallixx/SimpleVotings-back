from django.urls import path
from . import views
from .views import MyTokenObtainPairView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.register),
    path('polls/new', views.create_poll, name='create_poll'),
    path('polls/', views.get_polls, name='view_polls'),
    path('polls/<int:pk>/', views.get_poll, name='poll-detail'),
    path('polls/<int:pk>/edit/', views.edit_poll, name='poll-edit'),
    path('', views.getRoutes),
]