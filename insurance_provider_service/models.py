from django.db import models
from django.utils.translation import gettext_lazy as _
from auth_service.models import User # Assuming User model is in auth_service
from django.utils import timezone # Added for default value

class InsuranceProvider(models.Model):
    # User field can represent an admin account associated with the insurance company for system access
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='insurance_provider_liaison_profile')
    company_name = models.CharField(max_length=255, unique=True)
    # Official ID number of the insurance provider company (e.g., NAIC number or other regulatory ID)
    provider_id_number = models.CharField(max_length=50, unique=True, help_text=_("Official ID of the insurance company"))
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    # Potentially, fields for API integration if this service directly communicates with them for other purposes
    # For claim processing, insurance_service will handle specifics per policy.

    is_active = models.BooleanField(default=True, help_text=_("Is this provider currently active for new policies/claims?"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} ({self.provider_id_number})"

    class Meta:
        db_table = "insurance_provider_companies"
        verbose_name = _("Insurance Provider Company")
        verbose_name_plural = _("Insurance Provider Companies")
        ordering = ['company_name']

# PatientPolicy and InsuranceClaim models have been moved to 'insurance_service'
