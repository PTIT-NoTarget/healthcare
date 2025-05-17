from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InsuranceProviderViewSet

router = DefaultRouter()
router.register(r'insurance-providers', InsuranceProviderViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 