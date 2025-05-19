from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('doctor/', views.doctor_dashboard_view, name='doctor_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('appointments/', views.appointments_view, name='appointments'),
    path('patient-records/', views.patient_records_view, name='patient_records'),
    path('prescriptions/', views.prescriptions_view, name='prescriptions'),
    path('pharmacy/', views.pharmacy_view, name='pharmacy'),
    path('laboratory/', views.laboratory_view, name='laboratory'),
    path('patient-management/', views.patient_management_view, name='patient_management'),
    path('inventory/', views.inventory_view, name='inventory'),
    path('payments/', views.payments_view, name='payments'),
]

