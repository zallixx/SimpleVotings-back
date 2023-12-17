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
    path('users/<int:pk>/username/', views.get_author_name, name='get_author_name'),
    path('polls/<int:pk>/delete/', views.delete_poll, name='delete_poll'),
    path('complains/', views.get_complains, name='get_complains'),
    path('complains/<int:pk>/', views.get_complain, name='get_complain'),
    path('vote-history/', views.get_vote_history, name='get_vote_history'),
    path('settings/', views.get_user_data, name='get_user_data'),
    path('settings/edit/', views.edit_user_data, name='edit_user_data'),
    path('change_password/', views.change_password, name='change_password'),
    path('', views.getRoutes),
]
