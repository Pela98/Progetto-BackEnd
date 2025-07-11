




# fitness/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('workout/create/', views.WorkoutCreateView.as_view(), name='workout_create'),
    path('goal/update/', views.GoalCreateUpdateView.as_view(), name='goal_update'),
    path('my_progress_sheets/', views.UserProgressSheetListView.as_view(), name='user_progress_sheets'),
    path('progress_sheet/<int:pk>/', views.ProgressSheetDetailView.as_view(), name='progress_sheet_detail'),


]
