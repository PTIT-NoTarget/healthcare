from rest_framework import serializers
from .models import Prescription
import requests


class MedicationItemInputSerializer(serializers.Serializer):
    medicine_id = serializers.CharField(max_length=50)
    dosage = serializers.CharField(max_length=100)
    frequency = serializers.CharField(max_length=100)
    duration = serializers.CharField(max_length=100)
    instructions = serializers.CharField()


class MedicationItemOutputSerializer(serializers.Serializer):
    medicine_id = serializers.CharField(max_length=50)
    medicine_name = serializers.CharField(max_length=200, read_only=True)
    generic_name = serializers.CharField(max_length=200, read_only=True)
    dosage_form = serializers.CharField(max_length=50, read_only=True)
    strength = serializers.CharField(max_length=50, read_only=True)
    dosage = serializers.CharField(max_length=100)
    frequency = serializers.CharField(max_length=100)
    duration = serializers.CharField(max_length=100)
    instructions = serializers.CharField()


class PrescriptionSerializer(serializers.ModelSerializer):
    # Define service URLs directly in the class - fixed to match actual API structure
    BASE_URL = "http://localhost:8000/api"
    MEDICINE_SERVICE_URL = f"{BASE_URL}/medicines"
    DOCTOR_SERVICE_URL = f"{BASE_URL}/doctors"
    PATIENT_SERVICE_URL = f"{BASE_URL}/patients"
    
    id = serializers.SerializerMethodField()
    medications = MedicationItemInputSerializer(many=True, write_only=True)
    medication_details = serializers.SerializerMethodField(read_only=True)
    patient_name = serializers.SerializerMethodField(read_only=True)
    doctor_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['prescription_id', 'created_at', 'updated_at']
    
    def get_id(self, obj):
        """Return the prescription_id as the id field for API consistency"""
        return obj.prescription_id
    
    def get_medication_details(self, obj):
        """Fetch medication details from medicine service"""
        medication_details = []
        
        for medication in obj.medications:
            medicine_id = medication.get('medicine_id')
            try:
                # Try several formats to handle different API configurations
                # First try the base URL to list all medicines
                response = requests.get(f"{self.MEDICINE_SERVICE_URL}")
                
                if response.status_code == 200:
                    all_medicines = response.json()
                    # Find the medicine with matching ID
                    medicine_data = None
                    for med in all_medicines:
                        if str(med.get('id')) == medicine_id or str(med.get('_id')) == medicine_id:
                            medicine_data = med
                            break
                    
                    if medicine_data:
                        medication_detail = {
                            'medicine_id': medicine_id,
                            'medicine_name': medicine_data.get('name'),
                            'generic_name': medicine_data.get('generic_name'),
                            'dosage_form': medicine_data.get('dosage_form'),
                            'strength': medicine_data.get('strength'),
                            'dosage': medication.get('dosage'),
                            'frequency': medication.get('frequency'),
                            'duration': medication.get('duration'),
                            'instructions': medication.get('instructions')
                        }
                        medication_details.append(medication_detail)
                    else:
                        # Medicine not found in the list
                        medication_with_name = medication.copy()
                        medication_with_name['medicine_name'] = "Unknown Medicine"
                        medication_with_name['generic_name'] = "Unknown"
                        medication_with_name['dosage_form'] = "Unknown"
                        medication_with_name['strength'] = "Unknown"
                        medication_details.append(medication_with_name)
                else:
                    # If we can't fetch the list, return placeholder data
                    medication_with_name = medication.copy()
                    medication_with_name['medicine_name'] = "Unknown Medicine"
                    medication_with_name['generic_name'] = "Unknown"
                    medication_with_name['dosage_form'] = "Unknown"
                    medication_with_name['strength'] = "Unknown"
                    medication_details.append(medication_with_name)
            except Exception as e:
                # If API call fails, just return the original data with a placeholder name
                medication_with_name = medication.copy()
                medication_with_name['medicine_name'] = "Unknown Medicine"
                medication_with_name['generic_name'] = "Unknown"
                medication_with_name['dosage_form'] = "Unknown"
                medication_with_name['strength'] = "Unknown"
                medication_details.append(medication_with_name)
        
        return medication_details
    
    def get_patient_name(self, obj):
        """Fetch patient name from patient service"""
        try:
            # Query patient API to find the patient by user_id
            response = requests.get(f"{self.PATIENT_SERVICE_URL}?user_id={obj.patient_id}")
            if response.status_code == 200:
                patients_data = response.json()
                if patients_data and len(patients_data) > 0:
                    patient_data = patients_data[0]  # Get the first patient with matching user_id
                    # Try to get first name and last name from API response
                    first_name = patient_data.get('first_name', '')
                    last_name = patient_data.get('last_name', '')
                    
                    # If names are not in the patient data, fetch from auth service
                    if not first_name or not last_name:
                        try:
                            auth_url = f"{self.BASE_URL}/auth/internal/user/{obj.patient_id}"
                            auth_response = requests.get(auth_url)
                            if auth_response.status_code == 200:
                                user_data = auth_response.json()
                                first_name = user_data.get('first_name', '')
                                last_name = user_data.get('last_name', '')
                        except Exception:
                            pass
                    
                    return f"{first_name} {last_name}".strip() or "Unknown Patient"
        except Exception as e:
            pass
        return "Unknown Patient"
    
    def get_doctor_name(self, obj):
        """Fetch doctor name from doctor service"""
        try:
            # Query doctor API to find the doctor by user_id
            response = requests.get(f"{self.DOCTOR_SERVICE_URL}?user_id={obj.doctor_id}")
            if response.status_code == 200:
                doctors_data = response.json()
                if doctors_data and len(doctors_data) > 0:
                    doctor_data = doctors_data[0]  # Get the first doctor with matching user_id
                    # Try to get first name and last name from API response
                    first_name = doctor_data.get('first_name', '')
                    last_name = doctor_data.get('last_name', '')
                    
                    # If names are not in the doctor data, fetch from auth service
                    if not first_name or not last_name:
                        try:
                            auth_url = f"{self.BASE_URL}/auth/internal/user/{obj.doctor_id}"
                            auth_response = requests.get(auth_url)
                            if auth_response.status_code == 200:
                                user_data = auth_response.json()
                                first_name = user_data.get('first_name', '')
                                last_name = user_data.get('last_name', '')
                        except Exception:
                            pass
                    
                    return f"Dr. {first_name} {last_name}".strip() or "Unknown Doctor"
        except Exception as e:
            pass
        return "Unknown Doctor"
    
    def create(self, validated_data):
        medications_data = validated_data.pop('medications')
        
        # Create prescription with medication data directly
        prescription = Prescription.objects.create(
            **validated_data,
            medications=medications_data
        )
        
        return prescription
    
    def update(self, instance, validated_data):
        if 'medications' in validated_data:
            instance.medications = validated_data.pop('medications')
        
        for field, value in validated_data.items():
            setattr(instance, field, value)
        
        instance.save()
        return instance 