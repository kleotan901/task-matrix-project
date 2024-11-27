import pdb

from django.urls import path, include
from rest_framework import routers

from project.views import ProjectViewSet

app_name = "project"

router = routers.DefaultRouter()
router.register("projects", ProjectViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
