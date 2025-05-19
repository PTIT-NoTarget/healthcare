from django.shortcuts import render

def login_view(request):
    return render(request, 'login.html')

def home_view(request):
    return render(request, 'home.html')

def register_view(request):
    return render(request, 'register.html')

def doctor_dashboard_view(request):
    return render(request, 'doctor_dashboard.html')

def profile_view(request):
    return render(request, 'profile.html')

def appointments_view(request):
    return render(request, 'appointments.html')

def patient_records_view(request):
    return render(request, 'patient_records.html')

def prescriptions_view(request):
    return render(request, 'prescriptions.html')

def pharmacy_view(request):
    return render(request, 'pharmacy.html')

def laboratory_view(request):
    return render(request, 'laboratory.html')

def patient_management_view(request):
    return render(request, 'patient_management.html')

def inventory_view(request):
    return render(request, 'inventory.html')

def payments_view(request):
    return render(request, 'payments.html')

