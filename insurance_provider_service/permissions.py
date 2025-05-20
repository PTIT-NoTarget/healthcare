from rest_framework import permissions


class IsInsuranceProvider(permissions.BasePermission):
    """
    Custom permission to only allow insurance providers access.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get user_id from request.user
        user_id = request.user.id
        
        # Check if user is an insurance provider liaison
        try:
            from .models import InsuranceProvider
            return InsuranceProvider.objects.filter(user_id=user_id).exists()
        except:
            return False 