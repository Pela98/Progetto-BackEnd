




# fitness/urls.py

from django.urls import path
from .views import WorkoutCreateView

urlpatterns = [
    path('workout/create/', WorkoutCreateView.as_view(), name='workout_create'),

]
