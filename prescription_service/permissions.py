from rest_framework import permissions
from auth_service.models import UserRole


class IsDoctorUser(permissions.BasePermission):
    """
    Custom permission to only allow doctors to create prescriptions.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated and is a doctor
        return request.user.is_authenticated and request.user.role == UserRole.DOCTOR


class IsPrescriptionDoctor(permissions.BasePermission):
    """
    Custom permission to only allow doctors who created the prescription to modify it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated and is the doctor who created the prescription
        return request.user.is_authenticated and (
            request.user.role == UserRole.DOCTOR and 
            str(request.user.id) == obj.doctor_id
        )


class IsPrescriptionPatient(permissions.BasePermission):
    """
    Custom permission to only allow patients to access their own prescriptions.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated and is the patient for this prescription
        return request.user.is_authenticated and (
            request.user.role == UserRole.PATIENT and 
            str(request.user.id) == obj.patient_id
        )


class IsPharmacistUser(permissions.BasePermission):
    """
    Custom permission to only allow pharmacists to dispense prescriptions.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated and is a pharmacist
        return request.user.is_authenticated and request.user.role == UserRole.PHARMACIST 