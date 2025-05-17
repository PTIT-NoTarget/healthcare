from django.urls import path
from . import views

urlpatterns = [
    path('', views.NurseListView.as_view(), name='nurse-list'),
    path('create/', views.NurseCreateView.as_view(), name='nurse-create'),
    path('<int:pk>/', views.NurseDetailView.as_view(), name='nurse-detail'),
]

