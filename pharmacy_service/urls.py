from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PharmacyViewSet, InventoryViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'pharmacies', PharmacyViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 