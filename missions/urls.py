from django.urls import path
from .views import MissionBoardView, TaskListAPI

app_name = 'missions'

urlpatterns = [
    path('', MissionBoardView.as_view(), name='home'),
    path('api/tasks/', TaskListAPI.as_view(), name='get_tasks'),
]