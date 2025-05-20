from rest_framework import permissions


class IsLaboratoryTechnician(permissions.BasePermission):
    """
    Custom permission to only allow laboratory technicians access.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get user_id from request.user
        user_id = request.user.id
        
        # Check if user is a laboratory technician
        try:
            from .models import LaboratoryTechnician
            return LaboratoryTechnician.objects.filter(user_id=user_id).exists()
        except:
            return False 