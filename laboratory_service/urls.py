from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LaboratoryViewSet, LabTestViewSet, LabOrderViewSet, TestResultViewSet

router = DefaultRouter()
router.register(r'laboratories', LaboratoryViewSet)
router.register(r'tests', LabTestViewSet)
router.register(r'orders', LabOrderViewSet)
router.register(r'results', TestResultViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 