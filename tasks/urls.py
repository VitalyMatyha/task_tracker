from django.urls import path, include
from rest_framework.routers import DefaultRouter

from tasks.views import TaskViewSet, ImportantTasksView

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('tasks/important/', ImportantTasksView.as_view(), name='important-tasks'),
    path('', include(router.urls)),
]