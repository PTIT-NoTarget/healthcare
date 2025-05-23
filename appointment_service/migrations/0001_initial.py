# Generated by Django 3.2.25 on 2025-05-20 03:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_id', models.CharField(max_length=20, unique=True)),
                ('patient_id', models.CharField(max_length=50)),
                ('provider_id', models.CharField(max_length=50)),
                ('provider_type', models.CharField(choices=[('DOCTOR', 'Doctor'), ('NURSE', 'Nurse'), ('LAB_TECHNICIAN', 'Laboratory Technician')], max_length=20)),
                ('status', models.CharField(choices=[('SCHEDULED', 'Scheduled'), ('CONFIRMED', 'Confirmed'), ('CHECKED_IN', 'Checked In'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'), ('NO_SHOW', 'No Show')], default='SCHEDULED', max_length=20)),
                ('reason', models.TextField()),
                ('notes', models.TextField(blank=True, null=True)),
                ('created_by', models.CharField(max_length=50)),
                ('cancelled_by', models.CharField(blank=True, max_length=50, null=True)),
                ('cancellation_reason', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'appointments',
                'ordering': ['-time_slot__start_time'],
            },
        ),
        migrations.CreateModel(
            name='AppointmentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_id', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('duration_minutes', models.IntegerField()),
                ('color_code', models.CharField(default='#3498db', max_length=7)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'appointment_types',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RecurringPattern',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pattern_id', models.CharField(max_length=20, unique=True)),
                ('provider_id', models.CharField(max_length=50)),
                ('provider_type', models.CharField(choices=[('DOCTOR', 'Doctor'), ('NURSE', 'Nurse'), ('LAB_TECHNICIAN', 'Laboratory Technician')], max_length=20)),
                ('day_of_week', models.CharField(choices=[('MONDAY', 'Monday'), ('TUESDAY', 'Tuesday'), ('WEDNESDAY', 'Wednesday'), ('THURSDAY', 'Thursday'), ('FRIDAY', 'Friday'), ('SATURDAY', 'Saturday'), ('SUNDAY', 'Sunday')], max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('slot_duration_minutes', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'recurring_patterns',
                'ordering': ['day_of_week', 'start_time'],
            },
        ),
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reminder_type', models.CharField(choices=[('EMAIL', 'Email'), ('SMS', 'SMS'), ('PUSH', 'Push Notification')], max_length=20)),
                ('scheduled_time', models.DateTimeField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('SENT', 'Sent'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20)),
                ('sent_time', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'reminders',
                'ordering': ['scheduled_time'],
            },
        ),
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider_id', models.CharField(max_length=50)),
                ('provider_type', models.CharField(choices=[('DOCTOR', 'Doctor'), ('NURSE', 'Nurse'), ('LAB_TECHNICIAN', 'Laboratory Technician')], max_length=20)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('is_available', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'time_slots',
                'ordering': ['start_time'],
            },
        ),
        migrations.AddIndex(
            model_name='timeslot',
            index=models.Index(fields=['provider_id'], name='time_slots_provide_8f1403_idx'),
        ),
        migrations.AddIndex(
            model_name='timeslot',
            index=models.Index(fields=['start_time'], name='time_slots_start_t_a5ce22_idx'),
        ),
        migrations.AddIndex(
            model_name='timeslot',
            index=models.Index(fields=['is_available'], name='time_slots_is_avai_5556fe_idx'),
        ),
        migrations.AddField(
            model_name='reminder',
            name='appointment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='appointment_service.appointment'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='appointment_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='appointment_service.appointmenttype'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='time_slot',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='appointment', to='appointment_service.timeslot'),
        ),
        migrations.AddIndex(
            model_name='appointment',
            index=models.Index(fields=['patient_id'], name='appointment_patient_75a4eb_idx'),
        ),
        migrations.AddIndex(
            model_name='appointment',
            index=models.Index(fields=['provider_id'], name='appointment_provide_7523ed_idx'),
        ),
        migrations.AddIndex(
            model_name='appointment',
            index=models.Index(fields=['status'], name='appointment_status_9fecd6_idx'),
        ),
    ]
