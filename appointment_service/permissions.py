from rest_framework import permissions


class IsProvider(permissions.BasePermission):
    """
    Custom permission to only allow healthcare providers to manage their appointments and slots.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            'DOCTOR',
            'NURSE',
            'LAB_TECHNICIAN'
        ]


class IsAppointmentProvider(permissions.BasePermission):
    """
    Custom permission to only allow the provider of an appointment to manage it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.role in ['DOCTOR', 'NURSE', 'LAB_TECHNICIAN'] and
            str(request.user.id) == obj.provider_id
        )


class IsAppointmentPatient(permissions.BasePermission):
    """
    Custom permission to only allow patients to access their own appointments.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.role == 'PATIENT' and
            str(request.user.id) == obj.patient_id
        )


class IsPatient(permissions.BasePermission):
    """
    Custom permission to only allow patients to book appointments.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'PATIENT'


class IsAdministrator(permissions.BasePermission):
    """
    Custom permission to only allow administrators to perform certain actions.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMINISTRATOR'


class IsTimeSlotProvider(permissions.BasePermission):
    """
    Custom permission to only allow the provider of a time slot to manage it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.role in ['DOCTOR', 'NURSE', 'LAB_TECHNICIAN'] and
            str(request.user.id) == obj.provider_id
        )


class IsRecurringPatternProvider(permissions.BasePermission):
    """
    Custom permission to only allow the provider of a recurring pattern to manage it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.role in ['DOCTOR', 'NURSE', 'LAB_TECHNICIAN'] and
            str(request.user.id) == obj.provider_id
        )

