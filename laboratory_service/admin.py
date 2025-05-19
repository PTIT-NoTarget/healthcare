from django.contrib import admin
from .models import Laboratory, LabTest, LabOrder, LabOrderTest, TestResult


@admin.register(Laboratory)
class LaboratoryAdmin(admin.ModelAdmin):
    list_display = ('lab_id', 'name', 'department', 'location', 'contact_number', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('lab_id', 'name', 'department', 'location')
    readonly_fields = ('lab_id', 'created_at', 'updated_at')


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ('test_id', 'name', 'category', 'sample_type', 'price', 'turn_around_time', 'is_active')
    list_filter = ('category', 'sample_type', 'is_active')
    search_fields = ('test_id', 'name', 'description')
    readonly_fields = ('test_id', 'created_at', 'updated_at')


class LabOrderTestInline(admin.TabularInline):
    model = LabOrderTest
    extra = 1
    fields = ('test', 'status', 'notes')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'patient_id', 'doctor_id', 'laboratory', 'ordered_date', 'status', 'priority')
    list_filter = ('status', 'priority', 'laboratory', 'ordered_date')
    search_fields = ('order_id', 'patient_id', 'doctor_id', 'notes')
    readonly_fields = ('order_id', 'created_at', 'updated_at')
    inlines = [LabOrderTestInline]


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('result_id', 'get_test_name', 'get_patient_id', 'abnormal_flag', 'performed_by', 'performed_date')
    list_filter = ('abnormal_flag', 'performed_date')
    search_fields = ('result_id', 'comments', 'order_test__test__name')
    readonly_fields = ('result_id', 'created_at', 'updated_at')
    
    def get_test_name(self, obj):
        return obj.order_test.test.name
    get_test_name.short_description = 'Test Name'
    
    def get_patient_id(self, obj):
        return obj.order_test.order.patient_id
    get_patient_id.short_description = 'Patient ID'
