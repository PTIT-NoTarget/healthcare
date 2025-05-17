from rest_framework import permissions


class IsLaboratoryTechnician(permissions.BasePermission):
    """
    Custom permission to only allow laboratory technicians access.
    """
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'laboratory_technician') 