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

// Load appointments based on filters
async function loadAppointments(filters = {}) {
    try {
        let queryParams = new URLSearchParams(filters);
        const response = await fetch(`${API_BASE_URL}/appointments/?${queryParams}`);
        const appointments = await response.json();

        const appointmentsList = document.getElementById('appointmentsList');
        appointmentsList.innerHTML = '';

        appointments.forEach(appointment => {
            const appointmentHtml = `
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h5 class="card-title">Dr. ${appointment.provider_name}</h5>
                                <span class="badge bg-${getStatusBadgeColor(appointment.status)}">${appointment.status}</span>
                            </div>
                            <p class="card-text">
                                <i class="fas fa-calendar"></i> ${formatDateTime(appointment.time_slot.start_time)}<br>
                                <i class="fas fa-user"></i> Patient: ${appointment.patient_name}<br>
                                <i class="fas fa-notes-medical"></i> Reason: ${appointment.reason}
                            </p>
                            <div class="d-flex justify-content-end gap-2">
                                ${getAppointmentActions(appointment)}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            appointmentsList.insertAdjacentHTML('beforeend', appointmentHtml);
        });
    } catch (error) {
        console.error('Error loading appointments:', error);
        showErrorAlert('Failed to load appointments');
    }
}

// Get appointment action buttons based on status
function getAppointmentActions(appointment) {
    const actions = [];

    if (appointment.status === 'SCHEDULED') {
        actions.push(`
            <button class="btn btn-sm btn-outline-primary" onclick="editAppointment('${appointment.id}')">
                <i class="fas fa-edit"></i> Edit
            </button>
            <button class="btn btn-sm btn-outline-danger" onclick="cancelAppointment('${appointment.id}')">
                <i class="fas fa-times"></i> Cancel
            </button>
        `);
    } else if (appointment.status === 'CONFIRMED') {
        actions.push(`
            <button class="btn btn-sm btn-outline-success" onclick="checkInAppointment('${appointment.id}')">
                <i class="fas fa-check"></i> Check In
            </button>
        `);
    }

    return actions.join('');
}

// Get status badge color
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

// Handle appointment creation
document.getElementById('appointmentForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = {
        patient_id: document.getElementById('patientSelect').value,
        provider_id: document.getElementById('doctorSelect').value,
        provider_type: 'DOCTOR',
        appointment_type: 'CONSULTATION',
        time_slot: document.getElementById('appointmentTime').value,
        reason: document.getElementById('appointmentReason').value
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
            $('#newAppointmentModal').modal('hide');
            await loadAppointments();
            showSuccessAlert('Appointment scheduled successfully');
        } else {
            throw new Error('Failed to schedule appointment');
        }
    } catch (error) {
        console.error('Error creating appointment:', error);
        showErrorAlert('Failed to schedule appointment');
    }
});

// Handle filter changes
document.getElementById('dateFilter')?.addEventListener('change', (e) => {
    const filters = getActiveFilters();
    loadAppointments(filters);
});

document.getElementById('statusFilter')?.addEventListener('change', (e) => {
    const filters = getActiveFilters();
    loadAppointments(filters);
});

document.getElementById('doctorFilter')?.addEventListener('change', (e) => {
    const filters = getActiveFilters();
    loadAppointments(filters);
});

// Get active filters
function getActiveFilters() {
    const filters = {};

    const dateFilter = document.getElementById('dateFilter')?.value;
    const statusFilter = document.getElementById('statusFilter')?.value;
    const doctorFilter = document.getElementById('doctorFilter')?.value;

    if (dateFilter && dateFilter !== 'all') {
        const today = new Date();
        if (dateFilter === 'today') {
            filters.start_date = today.toISOString().split('T')[0];
            filters.end_date = today.toISOString().split('T')[0];
        } else if (dateFilter === 'week') {
            const weekLater = new Date(today.setDate(today.getDate() + 7));
            filters.start_date = new Date().toISOString().split('T')[0];
            filters.end_date = weekLater.toISOString().split('T')[0];
        } else if (dateFilter === 'month') {
            const monthLater = new Date(today.setMonth(today.getMonth() + 1));
            filters.start_date = new Date().toISOString().split('T')[0];
            filters.end_date = monthLater.toISOString().split('T')[0];
        }
    }

    if (statusFilter && statusFilter !== 'all') {
        filters.status = statusFilter.toUpperCase();
    }

    if (doctorFilter && doctorFilter !== 'all') {
        filters.provider_id = doctorFilter;
    }

    return filters;
}

// Load doctors for filter and new appointment form
async function loadDoctors() {
    try {
        const response = await fetch(`${API_BASE_URL}/doctors/`);
        const doctors = await response.json();

        const doctorFilter = document.getElementById('doctorFilter');
        const doctorSelect = document.getElementById('doctorSelect');

        doctors.forEach(doctor => {
            const option = new Option(`Dr. ${doctor.first_name} ${doctor.last_name}`, doctor.user_id);
            doctorFilter?.add(option.cloneNode(true));
            doctorSelect?.add(option);
        });
    } catch (error) {
        console.error('Error loading doctors:', error);
        showErrorAlert('Failed to load doctors list');
    }
}

async function loadPatients() {
    try {
        const response = await fetch(`${API_BASE_URL}/patients/`);
        const patients = await response.json();

        const patientSelect = document.getElementById('patientSelect');
        patientSelect.innerHTML = '<option value="">Select Patient</option>';

        patients.forEach(patient => {
            const option = new Option(
                `${patient.first_name} ${patient.last_name}`,
                patient.user_id
            );
            patientSelect.add(option);
        });
    } catch (error) {
        console.error('Error loading patients:', error);
        showErrorAlert('Failed to load patients list');
    }
}

// Cancel appointment
async function cancelAppointment(appointmentId) {
    if (!confirm('Are you sure you want to cancel this appointment?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/appointments/${appointmentId}/cancel/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify({
                cancellation_reason: 'Cancelled by user',
                cancelled_by: localStorage.getItem('userId')
            })
        });

        if (response.ok) {
            await loadAppointments(getActiveFilters());
            showSuccessAlert('Appointment cancelled successfully');
        } else {
            throw new Error('Failed to cancel appointment');
        }
    } catch (error) {
        console.error('Error cancelling appointment:', error);
        showErrorAlert('Failed to cancel appointment');
    }
}

// Check in appointment
async function checkInAppointment(appointmentId) {
    try {
        const response = await fetch(`${API_BASE_URL}/appointments/${appointmentId}/check_in/`, {
            method: 'POST'
        });

        if (response.ok) {
            await loadAppointments(getActiveFilters());
            showSuccessAlert('Patient checked in successfully');
        } else {
            throw new Error('Failed to check in patient');
        }
    } catch (error) {
        console.error('Error checking in patient:', error);
        showErrorAlert('Failed to check in patient');
    }
}

// UI helper functions
function showSuccessAlert(message) {
    // Implement your alert UI here
    alert(message);
}

function showErrorAlert(message) {
    // Implement your alert UI here
    alert(message);
}

// Initialize page
document.addEventListener('DOMContentLoaded', () => {
    loadDoctors();
    loadPatients();
    setupAvailableTimesListener();
    loadAppointments();
});

// Validate appointment form
function validateAppointmentForm() {
    const form = document.getElementById('appointmentForm');
    const patientSelect = document.getElementById('patientSelect');
    const doctorSelect = document.getElementById('doctorSelect');
    const appointmentDate = document.getElementById('appointmentDate');
    const appointmentTime = document.getElementById('appointmentTime');
    const appointmentReason = document.getElementById('appointmentReason');

    // Clear previous error messages
    clearFormErrors();

    let isValid = true;

    // Validate patient
    if (!patientSelect.value) {
        showFieldError(patientSelect, 'Please select a patient');
        isValid = false;
    }

    // Validate doctor
    if (!doctorSelect.value) {
        showFieldError(doctorSelect, 'Please select a doctor');
        isValid = false;
    }

    // Validate date
    if (!appointmentDate.value) {
        showFieldError(appointmentDate, 'Please select a date');
        isValid = false;
    } else {
        const selectedDate = new Date(appointmentDate.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (selectedDate < today) {
            showFieldError(appointmentDate, 'Cannot select a past date');
            isValid = false;
        }
    }

    // Validate time
    if (!appointmentTime.value) {
        showFieldError(appointmentTime, 'Please select a time');
        isValid = false;
    }

    // Validate reason
    if (!appointmentReason.value.trim()) {
        showFieldError(appointmentReason, 'Please provide a reason for the appointment');
        isValid = false;
    }

    return isValid;
}

// Show error message for a form field
function showFieldError(field, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.classList.add('is-invalid');
    field.parentNode.appendChild(errorDiv);
}

// Clear all form errors
function clearFormErrors() {
    const form = document.getElementById('appointmentForm');
    const invalidFields = form.querySelectorAll('.is-invalid');
    invalidFields.forEach(field => {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    });
}

// Update saveAppointment click handler
document.getElementById('saveAppointment').addEventListener('click', async () => {
    if (!validateAppointmentForm()) {
        return;
    }

    const form = document.getElementById('appointmentForm');
    const selectedTimeSlotId = document.getElementById('appointmentTime').value; // This will be the timeslot ID

    const formData = {
        patient_id: document.getElementById('patientSelect').value,
        provider_id: document.getElementById('doctorSelect').value,
        provider_type: 'DOCTOR',
        time_slot: selectedTimeSlotId, // Use the selected timeslot ID directly
        reason: document.getElementById('appointmentReason').value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/appointments/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify(formData),
        });

        if (response.ok) {
            $('#newAppointmentModal').modal('hide');
            await loadAppointments(getActiveFilters());
            showSuccessAlert('Appointment scheduled successfully');
            form.reset();
        } else {
            const error = await response.json();
            throw new Error(error.message || 'Failed to schedule appointment');
        }
    } catch (error) {
        console.error('Error creating appointment:', error);
        showErrorAlert(error.message || 'Failed to schedule appointment');
    }
});

// Show available time slots when date and doctor are selected
function setupAvailableTimesListener() {
    const dateInput = document.getElementById('appointmentDate');
    const doctorSelect = document.getElementById('doctorSelect');
    const timeInput = document.getElementById('appointmentTime');
    const timeSelectContainer = document.getElementById('timeSelectContainer');

    async function updateAvailableTimes() {
        if (!dateInput.value || !doctorSelect.value) {
            timeInput.innerHTML = '<option value="">Select a date and doctor first</option>';
            return;
        }

        try {
            // Show loading state
            timeInput.innerHTML = '<option value="">Loading available times...</option>';
            timeInput.disabled = true;

            const response = await fetch(
                `${API_BASE_URL}/appointments/timeslots/available/?` +
                `provider_id=${doctorSelect.value}&` +
                `provider_type=DOCTOR&` +
                `start_date=${dateInput.value}&` +
                `end_date=${dateInput.value}`
            );

            if (!response.ok) {
                throw new Error('Failed to fetch available time slots');
            }

            const slots = await response.json();

            if (slots.length === 0) {
                timeInput.innerHTML = '<option value="">No available slots for this date</option>';
                timeInput.disabled = true;
                return;
            }

            // Clear and populate time slots
            timeInput.innerHTML = '<option value="">Select a time</option>';
            timeInput.disabled = false;

            slots.forEach(slot => {
                const startTime = new Date(slot.start_time);
                const endTime = new Date(slot.end_time);

                const timeString = startTime.toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit',
                    hour12: false
                });

                const duration = Math.round((endTime - startTime) / (1000 * 60)); // Duration in minutes

                const option = new Option(
                    `${timeString} (${duration} min)`,
                    slot.id // Changed from timeString to slot.id
                );
                timeInput.add(option);
            });
        } catch (error) {
            console.error('Error loading available times:', error);
            timeInput.innerHTML = '<option value="">Error loading time slots</option>';
            timeInput.disabled = true;
            showErrorAlert('Failed to load available time slots');
        }
    }

    // Add event listeners
    dateInput.addEventListener('change', updateAvailableTimes);
    doctorSelect.addEventListener('change', updateAvailableTimes);

    // Initial update if both fields are already filled
    if (dateInput.value && doctorSelect.value) {
        updateAvailableTimes();
    }
}

