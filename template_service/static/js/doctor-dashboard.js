document.addEventListener('DOMContentLoaded', function() {
    // Load doctor's information
    loadDoctorInfo();
    // Load appointments
    loadTodayAppointments();
    // Load stats
    loadDashboardStats();
    // Load notifications
    loadNotifications();
    // Load patient records
    loadRecentPatientRecords();
    // Initialize form handlers
    initializeFormHandlers();

    // Load doctor information
    async function loadDoctorInfo() {
        try {
            const response = await fetch('/api/auth/profile/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const data = await response.json();
            document.getElementById('doctorName').textContent = data.name || data.username;

            // Load doctor's specialization
            const doctorResponse = await fetch(`/api/doctors/${data.id}/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const doctorData = await doctorResponse.json();
            document.getElementById('doctorSpecialization').textContent = doctorData.specialization;
        } catch (error) {
            console.error('Error loading doctor info:', error);
        }
    }

    // Load today's appointments
    async function loadTodayAppointments() {
        try {
            const today = new Date().toISOString().split('T')[0];
            const response = await fetch(`/api/appointments/doctor/?date=${today}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const appointments = await response.json();

            const appointmentsList = document.getElementById('appointmentsList');
            appointmentsList.innerHTML = '';

            appointments.forEach(appointment => {
                const appointmentElement = createAppointmentElement(appointment);
                appointmentsList.appendChild(appointmentElement);
            });
        } catch (error) {
            console.error('Error loading appointments:', error);
        }
    }

    // Create appointment element
    function createAppointmentElement(appointment) {
        const div = document.createElement('div');
        div.className = 'appointment-item p-3 mb-2 bg-light rounded';
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-0">${appointment.patient_name}</h6>
                    <small class="text-muted">${formatTime(appointment.time)}</small>
                </div>
                <div>
                    <span class="badge bg-${getStatusBadgeColor(appointment.status)}">${appointment.status}</span>
                </div>
            </div>
        `;
        return div;
    }

    // Load dashboard statistics
    async function loadDashboardStats() {
        try {
            const response = await fetch('/api/doctors/stats/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const stats = await response.json();

            document.getElementById('todayAppointments').textContent = stats.today_appointments;
            document.getElementById('treatedPatients').textContent = stats.patients_treated;
            document.getElementById('pendingReports').textContent = stats.pending_reports;
            document.getElementById('upcomingAppointments').textContent = stats.upcoming_appointments;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    // Load notifications
    async function loadNotifications() {
        try {
            const response = await fetch('/api/notifications/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const notifications = await response.json();

            const notificationsList = document.getElementById('notificationsList');
            notificationsList.innerHTML = '';

            notifications.forEach(notification => {
                const notificationElement = createNotificationElement(notification);
                notificationsList.appendChild(notificationElement);
            });
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    // Create notification element
    function createNotificationElement(notification) {
        const div = document.createElement('div');
        div.className = 'notification-item p-2 border-bottom';
        div.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-bell text-primary me-2"></i>
                <div>
                    <p class="mb-0">${notification.message}</p>
                    <small class="text-muted">${formatTimeAgo(notification.created_at)}</small>
                </div>
            </div>
        `;
        return div;
    }

    // Load recent patient records
    async function loadRecentPatientRecords() {
        try {
            const response = await fetch('/api/medical-records/recent/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const records = await response.json();

            const recordsList = document.getElementById('patientRecordsList');
            recordsList.innerHTML = '';

            records.forEach(record => {
                const recordElement = createRecordElement(record);
                recordsList.appendChild(recordElement);
            });
        } catch (error) {
            console.error('Error loading patient records:', error);
        }
    }

    // Create record element
    function createRecordElement(record) {
        const div = document.createElement('div');
        div.className = 'record-item p-3 border-bottom';
        div.innerHTML = `
            <div class="d-flex justify-content-between">
                <div>
                    <h6 class="mb-1">${record.patient_name}</h6>
                    <p class="mb-0 text-muted">${record.diagnosis}</p>
                </div>
                <small class="text-muted">${formatDate(record.date)}</small>
            </div>
        `;
        return div;
    }

    // Initialize form handlers
    function initializeFormHandlers() {
        // Handle new appointment form
        const appointmentForm = document.getElementById('appointmentForm');
        const saveAppointment = document.getElementById('saveAppointment');
        if (saveAppointment) {
            saveAppointment.addEventListener('click', handleNewAppointment);
        }

        // Handle prescription form
        const prescriptionForm = document.getElementById('prescriptionForm');
        const savePrescription = document.getElementById('savePrescription');
        if (savePrescription) {
            savePrescription.addEventListener('click', handleNewPrescription);
        }

        // Handle lab request form
        const labRequestForm = document.getElementById('labRequestForm');
        const saveLabRequest = document.getElementById('saveLabRequest');
        if (saveLabRequest) {
            saveLabRequest.addEventListener('click', handleNewLabRequest);
        }

        // Add medication button handler
        const addMedicationBtn = document.getElementById('addMedication');
        if (addMedicationBtn) {
            addMedicationBtn.addEventListener('click', addMedicationField);
        }
    }

    // Handle new appointment submission
    async function handleNewAppointment(e) {
        e.preventDefault();
        const form = document.getElementById('appointmentForm');
        const formData = new FormData(form);

        try {
            const response = await fetch('/api/appointments/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(Object.fromEntries(formData))
            });

            if (response.ok) {
                // Close modal and refresh appointments
                bootstrap.Modal.getInstance(document.getElementById('appointmentModal')).hide();
                loadTodayAppointments();
                showAlert('Appointment scheduled successfully!', 'success');
            } else {
                showAlert('Error scheduling appointment', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('Error scheduling appointment', 'danger');
        }
    }

    // Handle new prescription submission
    async function handleNewPrescription(e) {
        e.preventDefault();
        const form = document.getElementById('prescriptionForm');
        const formData = new FormData(form);

        try {
            const response = await fetch('/api/prescriptions/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(Object.fromEntries(formData))
            });

            if (response.ok) {
                bootstrap.Modal.getInstance(document.getElementById('prescriptionModal')).hide();
                showAlert('Prescription created successfully!', 'success');
            } else {
                showAlert('Error creating prescription', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('Error creating prescription', 'danger');
        }
    }

    // Handle new lab request submission
    async function handleNewLabRequest(e) {
        e.preventDefault();
        const form = document.getElementById('labRequestForm');
        const formData = new FormData(form);

        try {
            const response = await fetch('/api/lab-requests/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(Object.fromEntries(formData))
            });

            if (response.ok) {
                bootstrap.Modal.getInstance(document.getElementById('labRequestModal')).hide();
                showAlert('Lab request submitted successfully!', 'success');
            } else {
                showAlert('Error submitting lab request', 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('Error submitting lab request', 'danger');
        }
    }

    // Add new medication field to prescription form
    function addMedicationField() {
        const medicationsList = document.getElementById('medicationsList');
        const newMedication = document.querySelector('.medication-item').cloneNode(true);
        // Clear input values
        newMedication.querySelectorAll('input').forEach(input => input.value = '');
        newMedication.querySelector('select').value = '';
        medicationsList.appendChild(newMedication);
    }

    // Utility functions
    function formatTime(timeString) {
        return new Date(timeString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }

    function formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        return formatDate(dateString);
    }

    function getStatusBadgeColor(status) {
        const colors = {
            'pending': 'warning',
            'confirmed': 'success',
            'cancelled': 'danger',
            'completed': 'info'
        };
        return colors[status.toLowerCase()] || 'secondary';
    }

    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.container-fluid').insertAdjacentElement('afterbegin', alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    }
});
