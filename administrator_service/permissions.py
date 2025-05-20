from rest_framework import permissions


class IsAdministrator(permissions.BasePermission):
    """
    Custom permission to only allow administrators access.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get user_id from request.user
        user_id = request.user.id
        
        # Check if user is an administrator by querying the Administrator model
        try:
            from .models import Administrator
            return Administrator.objects.filter(user_id=user_id).exists()
        except:
            return False


class IsHighLevelAdministrator(permissions.BasePermission):
    """
    Permission for high-level administrative access (level 3+)
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get user_id from request.user
        user_id = request.user.id
        
        # Check if user is a high-level administrator
        try:
            from .models import Administrator
            admin = Administrator.objects.filter(user_id=user_id).first()
            return admin is not None and admin.access_level >= 3
        except:
            return False 