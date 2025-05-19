// Constants
const API_BASE_URL = '/api';

// Utility functions
const formatDateTime = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// Load doctor's information and dashboard stats
async function loadDoctorDashboard() {
    try {
        const doctorId = localStorage.getItem('doctorId');
        const response = await fetch(`${API_BASE_URL}/doctors/${doctorId}/dashboard_stats/`);
        const data = await response.json();

        // Update doctor info
        document.getElementById('doctorName').textContent = data.full_name;
        document.getElementById('doctorSpecialization').textContent = data.specialization;

        // Update statistics
        document.getElementById('todayAppointments').textContent = data.today_appointments;
        document.getElementById('treatedPatients').textContent = data.total_patients;
        document.getElementById('pendingReports').textContent = data.pending_reports;
        document.getElementById('upcomingAppointments').textContent = data.upcoming_appointments;

        await loadTodayAppointments();
        await loadRecentPatients();
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showErrorAlert('Failed to load dashboard information');
    }
}

// Load today's appointments
async function loadTodayAppointments() {
    try {
        const doctorId = localStorage.getItem('doctorId');
        const response = await fetch(`${API_BASE_URL}/doctors/${doctorId}/today_appointments/`);
        const appointments = await response.json();

        const appointmentsList = document.getElementById('appointmentsList');
        appointmentsList.innerHTML = '';

        appointments.forEach(appointment => {
            const appointmentHtml = `
                <div class="appointment-item p-3 mb-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">Patient: ${appointment.patient_name}</h6>
                            <p class="mb-1"><small>${formatDateTime(appointment.time_slot.start_time)}</small></p>
                            <p class="mb-1"><small>Reason: ${appointment.reason}</small></p>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-${getStatusBadgeColor(appointment.status)}">${appointment.status}</span>
                            <div class="mt-2">
                                <button class="btn btn-sm btn-outline-primary" onclick="updateAppointmentStatus('${appointment.id}', 'CHECKED_IN')">
                                    Check In
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            appointmentsList.insertAdjacentHTML('beforeend', appointmentHtml);
        });
    } catch (error) {
        console.error('Error loading appointments:', error);
        showErrorAlert('Failed to load today\'s appointments');
    }
}

// Load recent patient records
async function loadRecentPatients() {
    try {
        const doctorId = localStorage.getItem('doctorId');
        const response = await fetch(`${API_BASE_URL}/doctors/${doctorId}/recent_patients/`);
        const patients = await response.json();

        const patientRecordsList = document.getElementById('patientRecordsList');
        patientRecordsList.innerHTML = '';

        patients.forEach(record => {
            const recordHtml = `
                <div class="p-3 border-bottom">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${record.patient_name}</h6>
                            <p class="mb-1"><small>Last Visit: ${formatDateTime(record.time_slot.start_time)}</small></p>
                        </div>
                        <button class="btn btn-sm btn-outline-primary" onclick="viewPatientRecord('${record.patient_id}')">
                            View Record
                        </button>
                    </div>
                </div>
            `;
            patientRecordsList.insertAdjacentHTML('beforeend', recordHtml);
        });
    } catch (error) {
        console.error('Error loading patient records:', error);
        showErrorAlert('Failed to load recent patient records');
    }
}

// Update appointment status
async function updateAppointmentStatus(appointmentId, newStatus) {
    try {
        const response = await fetch(`${API_BASE_URL}/appointments/${appointmentId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            await loadTodayAppointments(); // Reload appointments
            showSuccessAlert('Appointment status updated successfully');
        } else {
            throw new Error('Failed to update appointment status');
        }
    } catch (error) {
        console.error('Error updating appointment:', error);
        showErrorAlert('Failed to update appointment status');
    }
}

// Handle new appointment creation
document.getElementById('appointmentForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        patient_id: document.getElementById('patientSelect').value,
        time_slot: document.getElementById('appointmentTime').value,
        reason: document.getElementById('appointmentNotes').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/appointments/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            $('#appointmentModal').modal('hide');
            await loadTodayAppointments();
            showSuccessAlert('Appointment scheduled successfully');
        } else {
            throw new Error('Failed to schedule appointment');
        }
    } catch (error) {
        console.error('Error creating appointment:', error);
        showErrorAlert('Failed to schedule appointment');
    }
});

// Utility functions for UI
function getStatusBadgeColor(status) {
    const statusColors = {
        'SCHEDULED': 'primary',
        'CONFIRMED': 'info',
        'CHECKED_IN': 'warning',
        'IN_PROGRESS': 'warning',
        'COMPLETED': 'success',
        'CANCELLED': 'danger',
        'NO_SHOW': 'secondary'
    };
    return statusColors[status] || 'primary';
}

function showSuccessAlert(message) {
    // Implement your alert UI here
    alert(message);
}

function showErrorAlert(message) {
    // Implement your alert UI here
    alert(message);
}
