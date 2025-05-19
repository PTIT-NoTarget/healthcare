from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InsuranceProviderViewSet

router = DefaultRouter()
router.register(r'companies', InsuranceProviderViewSet, basename='insuranceprovidercompany')
# Changed base route from 'providers' to 'companies' for clarity

urlpatterns = [
    path('', include(router.urls)),
]
