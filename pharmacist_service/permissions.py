from rest_framework import permissions


class IsPharmacist(permissions.BasePermission):
    """
    Custom permission to only allow pharmacists access.
    """
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'pharmacist') 