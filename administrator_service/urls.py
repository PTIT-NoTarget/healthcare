from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdministratorViewSet

router = DefaultRouter()
router.register(r'administrators', AdministratorViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 