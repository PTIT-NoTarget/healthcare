from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import PatientRegisterView, AdminCreateUserView, UserDetailView, ProfileUpdateView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', PatientRegisterView.as_view(), name='patient_register'),
    path('admin/create-user/', AdminCreateUserView.as_view(), name='admin_create_user'),
    path('profile/', UserDetailView.as_view(), name='user_profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
]
