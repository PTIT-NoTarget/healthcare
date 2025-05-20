from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from auth_service.models import User, UserRole, FullName, Address
from doctor_service.models import Doctor
from nurse_service.models import Nurse
from patient_service.models import Patient
from pharmacist_service.models import Pharmacist
from administrator_service.models import Administrator
from appointment_service.models import AppointmentType, TimeSlot
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        # Create Users first
        users = [
            # Doctors
            User.objects.create(
                username='dr.smith',
                password=make_password('password123'),
                email='smith@hospital.com',
                phone_number='1234567890',
                role=UserRole.DOCTOR
            ),
            User.objects.create(
                username='dr.jones',
                password=make_password('password123'),
                email='jones@hospital.com',
                phone_number='1234567891',
                role=UserRole.DOCTOR
            ),
            # Nurses
            User.objects.create(
                username='nurse.williams',
                password=make_password('password123'),
                email='williams@hospital.com',
                phone_number='1234567892',
                role=UserRole.NURSE
            ),
            User.objects.create(
                username='nurse.brown',
                password=make_password('password123'),
                email='brown@hospital.com',
                phone_number='1234567893',
                role=UserRole.NURSE
            ),
            # Patients
            User.objects.create(
                username='patient.johnson',
                password=make_password('password123'),
                email='johnson@email.com',
                phone_number='1234567894',
                role=UserRole.PATIENT
            ),
            User.objects.create(
                username='patient.davis',
                password=make_password('password123'),
                email='davis@email.com',
                phone_number='1234567895',
                role=UserRole.PATIENT
            ),
            # Pharmacists
            User.objects.create(
                username='pharm.wilson',
                password=make_password('password123'),
                email='wilson@pharmacy.com',
                phone_number='1234567896',
                role=UserRole.PHARMACIST
            ),
            User.objects.create(
                username='pharm.miller',
                password=make_password('password123'),
                email='miller@pharmacy.com',
                phone_number='1234567897',
                role=UserRole.PHARMACIST
            ),
            # Administrators
            User.objects.create(
                username='admin.taylor',
                password=make_password('password123'),
                email='taylor@hospital.com',
                phone_number='1234567898',
                role=UserRole.ADMINISTRATOR
            ),
            User.objects.create(
                username='admin.anderson',
                password=make_password('password123'),
                email='anderson@hospital.com',
                phone_number='1234567899',
                role=UserRole.ADMINISTRATOR
            ),
        ]

        # Create related records
        for user in users:
            # Create FullName
            FullName.objects.create(
                user=user,
                first_name=user.username.split('.')[1].title(),
                last_name='LastName',
                is_primary=True
            )

            # Create Address
            Address.objects.create(
                user=user,
                address=f"{123 + user.id} Main St, City, State 12345",
                is_primary=True
            )

            # Create role-specific records
            if user.role == UserRole.DOCTOR:
                Doctor.objects.create(
                    user_id=user.id,
                    specialization='General Medicine' if user.id % 2 == 0 else 'Cardiology',
                    license_number=f'DOC{1000 + user.id}'
                )
            elif user.role == UserRole.NURSE:
                Nurse.objects.create(
                    user_id=user.id,
                    department='Emergency' if user.id % 2 == 0 else 'Pediatrics',
                    nurse_id=f'NUR{2000 + user.id}'
                )
            elif user.role == UserRole.PATIENT:
                Patient.objects.create(
                    user_id=user.id,
                    date_of_birth=timezone.now() - timedelta(days=365 * 30),
                    blood_type='A+' if user.id % 2 == 0 else 'O-',
                    medical_history='No significant medical history',
                    emergency_contact='Emergency Contact Name: 123-456-7890'
                )
            elif user.role == UserRole.PHARMACIST:
                Pharmacist.objects.create(
                    user_id=user.id,
                    pharmacist_id=f'PHARM{3000 + user.id}',
                    license_number=f'LIC{4000 + user.id}',
                    specialization='Clinical Pharmacy' if user.id % 2 == 0 else 'Retail Pharmacy',
                    pharmacy_id=f'PHARMACY{100 + user.id}',
                    contact_phone=user.phone_number,
                    contact_email=user.email
                )
            elif user.role == UserRole.ADMINISTRATOR:
                Administrator.objects.create(
                    user_id=user.id,
                    employee_id=f'ADM{5000 + user.id}',
                    department='HR' if user.id % 2 == 0 else 'Operations',
                    access_level=3 if user.id % 2 == 0 else 2
                )

        # Create AppointmentTypes
        appointment_types = [
            AppointmentType.objects.create(
                type_id='CHECKUP',
                name='Regular Checkup',
                description='Routine medical examination',
                duration_minutes=30,
                color_code='#3498db'
            ),
            AppointmentType.objects.create(
                type_id='FOLLOWUP',
                name='Follow-up Visit',
                description='Follow-up consultation',
                duration_minutes=20,
                color_code='#2ecc71'
            ),
            AppointmentType.objects.create(
                type_id='EMERGENCY',
                name='Emergency Visit',
                description='Urgent medical attention',
                duration_minutes=45,
                color_code='#e74c3c'
            )
        ]

        self.stdout.write(self.style.SUCCESS('Successfully created sample data'))