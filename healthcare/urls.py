"""
URL configuration for healthcare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("template_service.urls")),  # Main application
    path("admin/", admin.site.urls),
    # Authentication Service
    path("api/auth/", include("auth_service.urls")),
    # Patient Service
    path("api/patients/", include("patient_service.urls")),
    # Doctor Service
    path("api/doctors/", include("doctor_service.urls")),
    # Nurse Service
    path("api/nurses/", include("nurse_service.urls")),
    # Administrator Service
    path("api/administrators/", include("administrator_service.urls")),
    # Pharmacist Service
    path("api/pharmacists/", include("pharmacist_service.urls")),
    # Insurance Provider Service
    path("api/insurance-providers/", include("insurance_provider_service.urls")),
    # Laboratory Technician Service
    path("api/lab-technicians/", include("laboratory_technician_service.urls")),
    # Medicine Service
    path("api/medicines/", include("medicine_service.urls")),
    # Pharmacy Service
    path("api/pharmacies/", include("pharmacy_service.urls")),
    # Inventory Service
    path("api/inventory/", include("inventory_service.urls")),
    # Payment Service
    path("api/payments/", include("payment_service.urls")),
    # Appointment Service
    path("api/appointments/", include("appointment_service.urls")),
    # Insurance Service
    path("api/insurance/", include("insurance_service.urls")),
    # Prescription Service
    path("api/prescriptions/", include("prescription_service.urls")),
    # Medical Record Service
    path("api/medical-records/", include("medical_record_service.urls")),
    # Laboratory Service
    path("api/laboratory/", include("laboratory_service.urls")),

]
