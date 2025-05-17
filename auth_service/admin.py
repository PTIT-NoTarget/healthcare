from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FullName, Address, UserRole

# Define an inline admin descriptor for FullName model
# which acts a bit like a singleton
class FullNameInline(admin.StackedInline):
    model = FullName
    can_delete = False
    verbose_name_plural = 'Full Names'
    fk_name = 'user'
    max_num = 1 # Assuming one primary full name per user

# Define an inline admin descriptor for Address model
class AddressInline(admin.StackedInline):
    model = Address
    can_delete = True
    verbose_name_plural = 'Addresses'
    fk_name = 'user'
    extra = 1 # Number of extra forms to display

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (FullNameInline, AddressInline)
    list_display = ('username', 'email', 'role', 'is_staff', 'created_at')
    list_filter = ('role', 'is_staff', 'created_at')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'phone_number')}), # Removed first_name, last_name as they are in FullName
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom Fields', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('email', 'phone_number', 'role',)}), # Added email here as well for creation form
    )
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

@admin.register(FullName)
class FullNameAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'is_primary', 'created_at')
    search_fields = ('user__username', 'first_name', 'last_name')
    list_filter = ('is_primary', 'created_at')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'is_primary', 'created_at')
    search_fields = ('user__username', 'address')
    list_filter = ('is_primary', 'created_at')

# Note: UserRole is an Enum and does not need to be registered with the admin directly.
# It's used as choices in the User model's role field.
