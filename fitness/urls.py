




# fitness/urls.py

from django.urls import path
from .views import UserListView, UserProgressSheetListView, ProgressSheetDetailView, WorkoutCreateView, \
    GoalCreateView, FeedbackCreateUpdateView, MarkGoalAchievedView

urlpatterns = [
    path('my_progress_sheets/', UserProgressSheetListView.as_view(), name='view_my_progress_sheets'),
    path('users/<int:user_pk>/progress_sheets/', UserProgressSheetListView.as_view(), name='view_user_progress_sheets'),
    path('goal/update/', GoalCreateView.as_view(), name='goal_update'),
    path('my_progress_sheets/', UserProgressSheetListView.as_view(), name='user_progress_sheets'),
    path('progress_sheet/<int:pk>/', ProgressSheetDetailView.as_view(), name='progress_sheet_detail'),
    path('workouts/<int:workout_pk>/feedback/', FeedbackCreateUpdateView.as_view(), name='feedback_create_update'),

    path('coach/all_users', UserListView.as_view(), name='user_list'),

    path('workouts/create/', WorkoutCreateView.as_view(), name='workout_create'),
    path('goals/<int:pk>/achieve/', MarkGoalAchievedView.as_view(), name='mark_goal_achieved'),


 #   path('achievements/', AchievedGoalsListView.as_view(), name='achieved_goals_list'),
]

