from rest_framework import permissions


class IsInsuranceProvider(permissions.BasePermission):
    """
    Custom permission to only allow insurance providers access.
    """
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'insurance_provider') 