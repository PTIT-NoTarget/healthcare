from rest_framework import permissions
from auth_service.models import UserRole


class IsMedicalProvider(permissions.BasePermission):
    """
    Custom permission to allow doctors, nurses, and administrators to access medical records.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            UserRole.DOCTOR, 
            UserRole.NURSE, 
            UserRole.ADMINISTRATOR,
            UserRole.LAB_TECHNICIAN
        ]


class IsPatientOwner(permissions.BasePermission):
    """
    Custom permission to only allow patients to access their own medical records.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.role == UserRole.PATIENT and 
            str(request.user.id) == obj.patient_id
        )


class IsRecordProvider(permissions.BasePermission):
    """
    Custom permission to only allow the provider who created the record to modify it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.role in [UserRole.DOCTOR, UserRole.NURSE] and 
            str(request.user.id) == obj.provider_id
        )


class IsAdministrator(permissions.BasePermission):
    """
    Custom permission to only allow administrators to perform certain actions.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ADMINISTRATOR 