from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from .task_generator import generate_tasks

class MissionBoardView(TemplateView):
    template_name = "missions/index.html"

class TaskListAPI(View):
    def get(self, request, *args, **kwargs):
        tasks = generate_tasks()
        return JsonResponse({'tasks': tasks})