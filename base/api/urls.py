from django.conf import settings
from django.conf.urls.static import static
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

    path('reset_password/', views.reset_password),
    path('reset_password/<uidb64>/<token>/', views.check_password_tokens),

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
    path('complains/all/', views.get_complains_unread, name='get_complains_unread'),
    path('complains/<int:pk>/', views.get_complain, name='get_complain'),
    path('complains/<int:pk>/set_answer/', views.set_answer_complain, name='set_answer_complain'),

    path('vote-history/', views.get_vote_history, name='get_vote_history'),

    path('settings/', views.get_user_data, name='get_user_data'),
    path('settings/edit/', views.edit_user_data, name='edit_user_data'),

    path('change_password/', views.change_password, name='change_password'),

    path('users/<int:pk>/', views.get_user, name='get_user'),
    path('user/delete/', views.delete_user, name='delete_user'),

    path('', views.getRoutes),
]