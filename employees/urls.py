from django.urls import path, include
from rest_framework.routers import DefaultRouter

from employees.views import EmployeeViewSet, BusyEmployeesView

router = DefaultRouter()
router.register('employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('employees/busy/', BusyEmployeesView.as_view(), name='busy-employees'),
    path('', include(router.urls)),
]
