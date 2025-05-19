from rest_framework import permissions
from auth_service.models import UserRole


class IsLabTechnician(permissions.BasePermission):
    """
    Custom permission to only allow lab technicians to access lab resources.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.LAB_TECHNICIAN


class IsDoctor(permissions.BasePermission):
    """
    Custom permission to only allow doctors to order tests.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.DOCTOR


class IsTestOrderDoctor(permissions.BasePermission):
    """
    Custom permission to only allow doctors who ordered the test to modify it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.role == UserRole.DOCTOR and 
            str(request.user.id) == obj.doctor_id
        )


class IsTestPatient(permissions.BasePermission):
    """
    Custom permission to only allow patients to access their own test results.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.role == UserRole.PATIENT and 
            str(request.user.id) == obj.patient_id
        )


class IsAdministrator(permissions.BasePermission):
    """
    Custom permission to only allow administrators to perform certain actions.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ADMINISTRATOR


class IsMedicalStaff(permissions.BasePermission):
    """
    Permission for all medical staff including doctors, nurses, and lab technicians.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            UserRole.DOCTOR,
            UserRole.NURSE,
            UserRole.LAB_TECHNICIAN,
            UserRole.ADMINISTRATOR
        ] 