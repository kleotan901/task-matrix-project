from django.urls import path
from task.views import TaskViewSet

app_name = "task"

urlpatterns = [
    path("", TaskViewSet.as_view({"get": "list", "post": "create"}), name="task-list"),
]
