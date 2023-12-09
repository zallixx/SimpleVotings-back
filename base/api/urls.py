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
    path('polls/new/', views.create_poll, name='create_poll'),
    path('polls/', views.get_polls, name='view_polls'),
    path('polls/<int:pk>/', views.get_poll, name='poll-detail'),
    path('polls/<int:pk>/edit/', views.edit_poll, name='poll-edit'),
    path('polls/<int:pk>/vote/', views.vote, name='vote'),
    path('polls/<int:pk>/complain/', views.complain, name='complain'),
    path('polls/<int:pk>/results/', views.results, name='results'),
    path('', views.getRoutes),
]