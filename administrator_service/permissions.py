from rest_framework import permissions


class IsAdministrator(permissions.BasePermission):
    """
    Custom permission to only allow administrators access.
    """
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'administrator')


class IsHighLevelAdministrator(permissions.BasePermission):
    """
    Permission for high-level administrative access (level 3+)
    """
    def has_permission(self, request, view):
        return (request.user and 
                hasattr(request.user, 'administrator') and 
                request.user.administrator.access_level >= 3) 