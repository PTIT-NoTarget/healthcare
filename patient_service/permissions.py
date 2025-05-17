from rest_framework import permissions

class IsPatientOwnerOrStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow patients to access only their own records
        if request.user.role == 'patient':
            return obj.user_id == request.user.id
        # Allow doctors, nurses and admin staff
        return request.user.role in ['doctor', 'nurse'] or request.user.is_staff

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
