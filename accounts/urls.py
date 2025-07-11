from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='profile_edit'),

 ]