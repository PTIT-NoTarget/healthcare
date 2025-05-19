from rest_framework import serializers
from .models import Prescription, MedicationItem


class MedicationItemSerializer(serializers.Serializer):
    medicine_id = serializers.CharField(max_length=50)
    medicine_name = serializers.CharField(max_length=200)
    dosage = serializers.CharField(max_length=100)
    frequency = serializers.CharField(max_length=100)
    duration = serializers.CharField(max_length=100)
    instructions = serializers.CharField()


class PrescriptionSerializer(serializers.ModelSerializer):
    medications = MedicationItemSerializer(many=True)
    
    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        medications_data = validated_data.pop('medications')
        prescription = Prescription.objects.create(**validated_data)
        
        # Add each medication item to the prescription
        prescription.medications = medications_data
        prescription.save()
        
        return prescription
    
    def update(self, instance, validated_data):
        if 'medications' in validated_data:
            medications_data = validated_data.pop('medications')
            instance.medications = medications_data
        
        for field, value in validated_data.items():
            setattr(instance, field, value)
        
        instance.save()
        return instance 