from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LaboratoryTechnicianViewSet

router = DefaultRouter()
router.register(r'laboratory-technicians', LaboratoryTechnicianViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 