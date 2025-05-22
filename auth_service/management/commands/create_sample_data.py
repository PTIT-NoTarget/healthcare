from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password
from auth_service.models import User, UserRole, FullName, Address
from patient_service.models import Patient
from doctor_service.models import Doctor
from nurse_service.models import Nurse
from administrator_service.models import Administrator
from pharmacist_service.models import Pharmacist
from laboratory_technician_service.models import LaboratoryTechnician
from insurance_provider_service.models import InsuranceProvider
from pharmacy_service.models import Pharmacy, Order, OrderItem
from laboratory_service.models import Laboratory, LabTest, LabOrder, LabOrderTest, TestResult
from medicine_service.models import Medicine
from medical_record_service.models import MedicalRecord
from prescription_service.models import Prescription
from appointment_service.models import TimeSlot, AppointmentType, Appointment
from payment_service.models import PaymentTransaction, InsuranceClaimProcessing
from insurance_service.models import PatientPolicy, InsuranceClaim


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        # Create Users
        users = self._create_users()
        
        # Create related service records
        patients = self._create_patients(users)
        doctors = self._create_doctors(users)
        nurses = self._create_nurses(users)
        admins = self._create_administrators(users)
        pharmacists = self._create_pharmacists(users)
        lab_techs = self._create_lab_technicians(users)
        insurance_providers = self._create_insurance_providers()
        
        # Create other related records
        pharmacies = self._create_pharmacies(pharmacists)
        laboratories = self._create_laboratories()
        medicines = self._create_medicines()
        appointments = self._create_appointments(patients, doctors)
        medical_records = self._create_medical_records(patients, doctors)
        prescriptions = self._create_prescriptions(patients, doctors, medicines)
        orders = self._create_pharmacy_orders(patients, doctors, pharmacies, medicines)
        lab_orders = self._create_lab_orders(patients, doctors, laboratories)
        
        # Create insurance related records
        policies = self._create_patient_policies(patients, insurance_providers)
        payments = self._create_payment_transactions(patients, orders)
        claims = self._create_insurance_claims(policies, payments)

        self.stdout.write(self.style.SUCCESS('Successfully created sample data'))

    def _create_users(self):
        users = []
        roles = [
            ('patient1', UserRole.PATIENT),
            ('patient2', UserRole.PATIENT),
            ('doctor1', UserRole.DOCTOR),
            ('doctor2', UserRole.DOCTOR),
            ('nurse1', UserRole.NURSE),
            ('admin1', UserRole.ADMINISTRATOR),
            ('pharm1', UserRole.PHARMACIST),
            ('labtech1', UserRole.LAB_TECHNICIAN),
        ]

        for username, role in roles:
            user = User.objects.create(
                username=username,
                email=f'{username}@example.com',
                password=make_password('password123'),
                role=role,
                phone_number=f'+1555{str(hash(username))[-4:]}',
            )
            
            # Create FullName
            FullName.objects.create(
                user=user,
                first_name=username.capitalize(),
                last_name='Test',
                is_primary=True
            )
            
            # Create Address
            Address.objects.create(
                user=user,
                address=f'{hash(username)%100} Main St, Test City, TS 12345',
                is_primary=True
            )
            
            users.append(user)
        
        return users

    def _create_patients(self, users):
        patients = []
        for user in users:
            if user.role == UserRole.PATIENT:
                patient = Patient.objects.create(
                    user_id=user.id,
                    date_of_birth=timezone.now() - timedelta(days=365*30),
                    blood_type='A+',
                    medical_history='No significant medical history',
                    emergency_contact='Emergency Contact: +1555-0000'
                )
                patients.append(patient)
        return patients

    def _create_doctors(self, users):
        doctors = []
        specializations = ['Cardiology', 'Pediatrics']
        i = 0
        for user in users:
            if user.role == UserRole.DOCTOR:
                doctor = Doctor.objects.create(
                    user_id=user.id,
                    specialization=specializations[i],
                    license_number=f'DOC{user.id}2023'
                )
                doctors.append(doctor)
                i += 1
        return doctors

    def _create_nurses(self, users):
        nurses = []
        for user in users:
            if user.role == UserRole.NURSE:
                nurse = Nurse.objects.create(
                    user_id=user.id,
                    department='Emergency',
                    nurse_id=f'N{user.id}2023'
                )
                nurses.append(nurse)
        return nurses

    def _create_administrators(self, users):
        admins = []
        for user in users:
            if user.role == UserRole.ADMINISTRATOR:
                admin = Administrator.objects.create(
                    user_id=user.id,
                    employee_id=f'ADM{user.id}2023',
                    department='IT',
                    access_level=2
                )
                admins.append(admin)
        return admins

    def _create_pharmacists(self, users):
        pharmacists = []
        for user in users:
            if user.role == UserRole.PHARMACIST:
                pharmacist = Pharmacist.objects.create(
                    user_id=user.id,
                    pharmacist_id=f'PH{user.id}2023',
                    license_number=f'PHAR{user.id}2023',
                    specialization='General',
                    contact_email=user.email
                )
                pharmacists.append(pharmacist)
        return pharmacists

    def _create_lab_technicians(self, users):
        lab_techs = []
        for user in users:
            if user.role == UserRole.LAB_TECHNICIAN:
                lab_tech = LaboratoryTechnician.objects.create(
                    user_id=user.id,
                    employee_id=f'LT{user.id}2023',
                    specialization='Blood Analysis',
                    laboratory_name='Central Lab',
                    certification='Certified Lab Technician'
                )
                lab_techs.append(lab_tech)
        return lab_techs

    def _create_insurance_providers(self):
        providers = []
        for i in range(2):
            provider = InsuranceProvider.objects.create(
                company_name=f'Insurance Co {i+1}',
                provider_id_number=f'INS{i+1}2023',
                contact_email=f'contact{i+1}@insurance{i+1}.com',
                contact_phone=f'+1555{i+1}000000',
                address=f'{i+1} Insurance Ave, Insurance City, IC 12345',
                website=f'https://insurance{i+1}.com'
            )
            providers.append(provider)
        return providers

    def _create_pharmacies(self, pharmacists):
        pharmacies = []
        for i in range(2):
            pharmacy = Pharmacy.objects.create(
                name=f'Pharmacy {i+1}',
                address=f'{i+1} Pharmacy St',
                city='Test City',
                state='TS',
                zip_code='12345',
                phone=f'+1555{i+1}111111',
                email=f'pharmacy{i+1}@example.com',
                license_number=f'PHAR{i+1}2023',
                hours_of_operation={'Mon-Fri': '9:00-18:00'},
                pharmacist_ids=[pharmacist.pharmacist_id for pharmacist in pharmacists]
            )
            pharmacies.append(pharmacy)
        return pharmacies

    def _create_laboratories(self):
        labs = []
        for i in range(2):
            lab = Laboratory.objects.create(
                lab_id=f'LAB{i+1}2023',
                name=f'Laboratory {i+1}',
                department='General',
                location=f'Floor {i+1}',
                contact_number=f'+1555{i+1}222222',
                email=f'lab{i+1}@example.com',
                description=f'General Laboratory {i+1}'
            )
            labs.append(lab)
        return labs

    def _create_medicines(self):
        medicines = []
        for i in range(2):
            medicine = Medicine.objects.create(
                name=f'Medicine {i+1}',
                generic_name=f'Generic Medicine {i+1}',
                manufacturer=f'Manufacturer {i+1}',
                description=f'Description for Medicine {i+1}',
                dosage_form='tablet',
                strength=f'{(i+1)*100}mg',
                ndc_code=f'NDC{i+1}2023',
                price=10.00 * (i+1),
                requires_prescription=True,
                side_effects=['headache', 'nausea'],
                interactions=['alcohol'],
                contraindications=['pregnancy'],
                active_ingredients=['ingredient1', 'ingredient2']
            )
            medicines.append(medicine)
        return medicines

    def _create_appointments(self, patients, doctors):
        appointments = []
        
        # First create appointment types
        app_type = AppointmentType.objects.create(
            type_id='GEN_CHECKUP',
            name='General Checkup',
            description='Regular medical checkup',
            duration_minutes=30,
            color_code='#3498db'
        )

        # Create time slots
        for doctor in doctors:
            time_slot = TimeSlot.objects.create(
                provider_id=str(doctor.user_id),
                provider_type='DOCTOR',
                start_time=timezone.now() + timedelta(days=1),
                end_time=timezone.now() + timedelta(days=1, minutes=30)
            )

            # Create appointment
            appointment = Appointment.objects.create(
                appointment_id=f'APT{doctor.user_id}2023',
                patient_id=str(patients[0].user_id),
                provider_id=str(doctor.user_id),
                provider_type='DOCTOR',
                appointment_type=app_type,
                time_slot=time_slot,
                reason='Regular checkup',
                created_by=str(patients[0].user_id)
            )
            appointments.append(appointment)
        
        return appointments

    def _create_medical_records(self, patients, doctors):
        records = []
        for patient in patients:
            record = MedicalRecord.objects.create(
                record_id=f'REC{patient.user_id}2023',
                patient_id=str(patient.user_id),
                visit_date=timezone.now(),
                visit_type='INITIAL',
                provider_id=str(doctors[0].user_id),
                chief_complaint='General checkup',
                diagnosis='Healthy',
                treatment_plan='Regular exercise',
                allergies=['none'],
                medications=['none'],
                procedures=['basic checkup'],
                lab_results=[],
                status='COMPLETED'
            )
            records.append(record)
        return records

    def _create_prescriptions(self, patients, doctors, medicines):
        prescriptions = []
        for patient in patients:
            prescription = Prescription.objects.create(
                prescription_id=f'PRES{patient.user_id}2023',
                patient_id=str(patient.user_id),
                doctor_id=str(doctors[0].user_id),
                diagnosis='Regular treatment',
                medications=[{
                    'medicine_id': str(medicines[0].id),
                    'medicine_name': medicines[0].name,
                    'dosage': '1 tablet',
                    'frequency': 'twice daily',
                    'duration': '7 days',
                    'instructions': 'Take with food'
                }]
            )
            prescriptions.append(prescription)
        return prescriptions

    def _create_pharmacy_orders(self, patients, doctors, pharmacies, medicines):
        orders = []
        for patient in patients:
            order = Order.objects.create(
                pharmacy=pharmacies[0],
                patient_id=str(patient.user_id),
                patient_name=f'Patient {patient.user_id}',
                doctor_id=str(doctors[0].user_id),
                doctor_name=f'Doctor {doctors[0].user_id}',
                total_amount=100.00,
                status='processing'
            )
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                inventory_item_id=str(medicines[0].id),
                medicine_name=medicines[0].name,
                quantity=1,
                unit_price=medicines[0].price,
                total_price=medicines[0].price
            )
            
            orders.append(order)
        return orders

    def _create_lab_orders(self, patients, doctors, laboratories):
        orders = []
        for patient in patients:
            # Create lab test
            test = LabTest.objects.create(
                test_id=f'TEST{patient.user_id}2023',
                name='Blood Test',
                category='Hematology',
                description='Complete Blood Count',
                price=50.00,
                turn_around_time=24,
                sample_type='Blood'
            )

            # Create lab order
            order = LabOrder.objects.create(
                order_id=f'LAB{patient.user_id}2023',
                patient_id=str(patient.user_id),
                doctor_id=str(doctors[0].user_id),
                laboratory=laboratories[0],
                status='COMPLETED'
            )

            # Create lab order test
            lab_order_test = LabOrderTest.objects.create(
                order=order,
                test=test,
                status='COMPLETED'
            )

            # Create test result
            TestResult.objects.create(
                result_id=f'RES{patient.user_id}2023',
                order_test=lab_order_test,
                result_value='Normal',
                unit='N/A',
                reference_range='Normal range',
                performed_by='LT12023'
            )

            orders.append(order)
        return orders

    def _create_patient_policies(self, patients, insurance_providers):
        policies = []
        for patient in patients:
            policy = PatientPolicy.objects.create(
                patient_id=str(patient.user_id),
                insurance_provider_company_id=str(insurance_providers[0].id),
                policy_number=f'POL{patient.user_id}2023',
                policy_holder_name=f'Patient {patient.user_id}',
                effective_date=timezone.now().date(),
                expiration_date=timezone.now().date() + timedelta(days=365),
                status='active',
                coverage_details={
                    'deductible_total': 1000,
                    'deductible_met': 0,
                    'co_pay_percentage': 20,
                    'out_of_pocket_max': 5000
                }
            )
            policies.append(policy)
        return policies

    def _create_payment_transactions(self, patients, orders):
        transactions = []
        for order in orders:
            transaction = PaymentTransaction.objects.create(
                patient_id=order.patient_id,
                service_type='pharmacy',
                originating_service_record_id=str(order.id),
                total_amount=order.total_amount,
                amount_covered_by_insurance=80.00,
                amount_due_by_patient=20.00,
                payment_status='completed',
                transaction_details={
                    'items': [{
                        'name': item.medicine_name,
                        'quantity': item.quantity,
                        'price': float(item.unit_price)
                    } for item in order.items.all()]
                }
            )
            transactions.append(transaction)
        return transactions

    def _create_insurance_claims(self, policies, payments):
        claims = []
        for policy, payment in zip(policies, payments):
            claim = InsuranceClaim.objects.create(
                policy=policy,
                payment_transaction_id=str(payment.id),
                service_date_start=timezone.now().date(),
                billed_amount=payment.total_amount,
                claimed_amount=payment.amount_covered_by_insurance,
                approved_amount=payment.amount_covered_by_insurance,
                patient_responsibility_amount=payment.amount_due_by_patient,
                status='closed_paid',
                claimed_items_details=payment.transaction_details
            )
            claims.append(claim)
        return claims

