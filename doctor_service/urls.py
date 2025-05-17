from django.urls import path
from . import views

urlpatterns = [
    path('', views.DoctorListView.as_view(), name='doctor-list'),
    path('create/', views.DoctorCreateView.as_view(), name='doctor-create'),
    path('<int:pk>/', views.DoctorDetailView.as_view(), name='doctor-detail'),
]
