from rest_framework import serializers
from .models import MedicalRecord, VitalSign, Note, Attachment


class VitalSignSerializer(serializers.Serializer):
    temperature = serializers.FloatField(required=False, allow_null=True)
    heart_rate = serializers.IntegerField(required=False, allow_null=True)
    blood_pressure_systolic = serializers.IntegerField(required=False, allow_null=True)
    blood_pressure_diastolic = serializers.IntegerField(required=False, allow_null=True)
    respiratory_rate = serializers.IntegerField(required=False, allow_null=True)
    oxygen_saturation = serializers.IntegerField(required=False, allow_null=True)
    height = serializers.FloatField(required=False, allow_null=True)
    weight = serializers.FloatField(required=False, allow_null=True)
    bmi = serializers.FloatField(required=False, allow_null=True)
    timestamp = serializers.DateTimeField(read_only=True)


class NoteSerializer(serializers.Serializer):
    note_type = serializers.CharField(max_length=50)
    content = serializers.CharField()
    author = serializers.CharField(max_length=50)
    timestamp = serializers.DateTimeField(read_only=True)


class AttachmentSerializer(serializers.Serializer):
    file_name = serializers.CharField(max_length=255)
    file_type = serializers.CharField(max_length=50)
    description = serializers.CharField(required=False, allow_null=True)
    file_url = serializers.URLField()
    uploaded_by = serializers.CharField(max_length=50)
    uploaded_at = serializers.DateTimeField(read_only=True)


class MedicalRecordSerializer(serializers.ModelSerializer):
    vital_signs = VitalSignSerializer(many=True, required=False)
    notes = NoteSerializer(many=True, required=False)
    attachments = AttachmentSerializer(many=True, required=False)
    allergies = serializers.ListField(child=serializers.CharField(), required=False)
    medications = serializers.ListField(child=serializers.CharField(), required=False)
    procedures = serializers.ListField(child=serializers.CharField(), required=False)
    lab_results = serializers.ListField(child=serializers.CharField(), required=False)
    
    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ['record_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Handle embedded data
        vital_signs_data = validated_data.pop('vital_signs', [])
        notes_data = validated_data.pop('notes', [])
        attachments_data = validated_data.pop('attachments', [])
        
        # Create the medical record
        medical_record = MedicalRecord.objects.create(**validated_data)
        
        # Add embedded documents
        if vital_signs_data:
            medical_record.vital_signs = vital_signs_data
        
        if notes_data:
            medical_record.notes = notes_data
        
        if attachments_data:
            medical_record.attachments = attachments_data
        
        medical_record.save()
        return medical_record
    
    def update(self, instance, validated_data):
        # Handle embedded data
        if 'vital_signs' in validated_data:
            instance.vital_signs = validated_data.pop('vital_signs')
        
        if 'notes' in validated_data:
            instance.notes = validated_data.pop('notes')
        
        if 'attachments' in validated_data:
            instance.attachments = validated_data.pop('attachments')
        
        # Handle list fields
        if 'allergies' in validated_data:
            instance.allergies = validated_data.pop('allergies')
        
        if 'medications' in validated_data:
            instance.medications = validated_data.pop('medications')
        
        if 'procedures' in validated_data:
            instance.procedures = validated_data.pop('procedures')
        
        if 'lab_results' in validated_data:
            instance.lab_results = validated_data.pop('lab_results')
        
        # Update the remaining fields
        for field, value in validated_data.items():
            setattr(instance, field, value)
        
        instance.save()
        return instance 