from rest_framework import serializers
from .models import Laboratory, LabTest, LabOrder, LabOrderTest, TestResult


class LaboratorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratory
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class LabTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class LabOrderTestSerializer(serializers.ModelSerializer):
    test_details = LabTestSerializer(source='test', read_only=True)
    result = TestResultSerializer(read_only=True)
    
    class Meta:
        model = LabOrderTest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class LabOrderTestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabOrderTest
        fields = ['test', 'notes']


class LabOrderSerializer(serializers.ModelSerializer):
    tests = LabOrderTestSerializer(many=True, read_only=True)
    laboratory_details = LaboratorySerializer(source='laboratory', read_only=True)
    
    class Meta:
        model = LabOrder
        fields = '__all__'
        read_only_fields = ['order_id', 'created_at', 'updated_at']


class LabOrderCreateSerializer(serializers.ModelSerializer):
    tests = LabOrderTestCreateSerializer(many=True, required=True)
    
    class Meta:
        model = LabOrder
        fields = ['patient_id', 'doctor_id', 'laboratory', 'scheduled_date', 'priority', 'notes', 'clinical_information', 'tests']
        read_only_fields = ['order_id']
    
    def create(self, validated_data):
        tests_data = validated_data.pop('tests')
        lab_order = LabOrder.objects.create(**validated_data)
        
        for test_data in tests_data:
            LabOrderTest.objects.create(order=lab_order, **test_data)
        
        return lab_order


class TestResultCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ['order_test', 'result_value', 'unit', 'reference_range', 'abnormal_flag', 'comments', 'performed_by']
        read_only_fields = ['result_id', 'performed_date'] 