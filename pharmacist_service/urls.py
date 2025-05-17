from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PharmacistViewSet

router = DefaultRouter()
router.register(r'pharmacists', PharmacistViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 