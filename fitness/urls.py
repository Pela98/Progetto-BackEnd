




# fitness/urls.py
from . import views
from django.urls import path
from .views import UserListView, UserProgressSheetListView, ProgressSheetDetailView, WorkoutCreateView, \
    FeedbackCreateUpdateView, UserGoalsListView

urlpatterns = [
    path('my_progress_sheets/', UserProgressSheetListView.as_view(), name='view_my_progress_sheets'),
    path('users/<int:user_pk>/progress_sheets/', UserProgressSheetListView.as_view(), name='view_user_progress_sheets'),
    path('my_progress_sheets/', UserProgressSheetListView.as_view(), name='user_progress_sheets'),
    path('progress_sheet/<int:pk>/', ProgressSheetDetailView.as_view(), name='progress_sheet_detail'),
    path('workouts/<int:workout_pk>/feedback/', FeedbackCreateUpdateView.as_view(), name='feedback_create_update'),

    path('coach/all_users/', UserListView.as_view(), name='user_list'),

    path('workouts/create/', WorkoutCreateView.as_view(), name='workout_create'),
    path('goals/create/', views.GoalCreateView.as_view(), name='goal_create'),
    path('goals/<int:pk>/update/', views.GoalUpdateView.as_view(), name='goal_update'),
    path('goals/<int:pk>/achieve/', views.achieve_goal, name='achieve_goal'),
    path('goals/achieved/', views.AchievedGoalsListView.as_view(), name='achieved_goals_list'),
    path('goals/unachieved/', views.UnachievedGoalsListView.as_view(), name='unachieved_goals_list'),
    path('users/<int:user_pk>/goals/', UserGoalsListView.as_view(), name='view_user_goals'),


 #   path('achievements/', AchievedGoalsListView.as_view(), name='achieved_goals_list'),
]

