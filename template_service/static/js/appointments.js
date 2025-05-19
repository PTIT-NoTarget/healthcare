document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const appointmentsList = document.getElementById('appointmentsList');
    const appointmentForm = document.getElementById('appointmentForm');
    const saveAppointmentBtn = document.getElementById('saveAppointment');
    const dateFilter = document.getElementById('dateFilter');
    const statusFilter = document.getElementById('statusFilter');
    const doctorFilter = document.getElementById('doctorFilter');
    const doctorSelect = document.getElementById('doctorSelect');

    // Load initial data
    loadDoctors();
    loadAppointments();

    // Event listeners
    dateFilter.addEventListener('change', filterAppointments);
    statusFilter.addEventListener('change', filterAppointments);
    doctorFilter.addEventListener('change', filterAppointments);
    saveAppointmentBtn.addEventListener('click', saveAppointment);

    // Function to load doctors for the dropdown
    async function loadDoctors() {
        try {
            const response = await fetch('/api/doctors/');
            const doctors = await response.json();

            // Populate doctor select in filters
            const filterOptions = doctors.map(doctor =>
                `<option value="${doctor.id}">${doctor.name}</option>`
            );
            doctorFilter.innerHTML += filterOptions.join('');

            // Populate doctor select in new appointment form
            doctorSelect.innerHTML = filterOptions.join('');
        } catch (error) {
            console.error('Error loading doctors:', error);
        }
    }

    // Function to load appointments
    async function loadAppointments() {
        try {
            const response = await fetch('/api/appointments/');
            const appointments = await response.json();
            displayAppointments(appointments);
        } catch (error) {
            console.error('Error loading appointments:', error);
        }
    }

    // Function to display appointments
    function displayAppointments(appointments) {
        appointmentsList.innerHTML = appointments.map(appointment => `
            <div class="col-md-6 mb-3">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <h5 class="card-title">Dr. ${appointment.doctor_name}</h5>
                            <span class="badge bg-${getStatusBadgeClass(appointment.status)}">${appointment.status}</span>
                        </div>
                        <p class="card-text">
                            <i class="fas fa-calendar"></i> ${formatDateTime(appointment.datetime)}<br>
                            <i class="fas fa-user"></i> Patient: ${appointment.patient_name}<br>
                            <i class="fas fa-notes-medical"></i> Reason: ${appointment.reason}
                        </p>
                        <div class="d-flex justify-content-end gap-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="editAppointment(${appointment.id})">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger" onclick="cancelAppointment(${appointment.id})">
                                <i class="fas fa-times"></i> Cancel
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Function to save new appointment
    async function saveAppointment() {
        const formData = {
            doctor_id: doctorSelect.value,
            date: document.getElementById('appointmentDate').value,
            time: document.getElementById('appointmentTime').value,
            reason: document.getElementById('appointmentReason').value
        };

        try {
            const response = await fetch('/api/appointments/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                // Close modal and reload appointments
                const modal = bootstrap.Modal.getInstance(document.getElementById('newAppointmentModal'));
                modal.hide();
                loadAppointments();
                appointmentForm.reset();
            } else {
                throw new Error('Failed to save appointment');
            }
        } catch (error) {
            console.error('Error saving appointment:', error);
            alert('Failed to save appointment. Please try again.');
        }
    }

    // Helper function to format date and time
    function formatDateTime(datetime) {
        return new Date(datetime).toLocaleString();
    }

    // Helper function to get badge class based on status
    function getStatusBadgeClass(status) {
        const statusClasses = {
            'scheduled': 'primary',
            'completed': 'success',
            'canceled': 'danger'
        };
        return statusClasses[status.toLowerCase()] || 'secondary';
    }

    // Function to filter appointments
    function filterAppointments() {
        // Implementation will be added based on backend API
        loadAppointments();
    }
});

// Function to edit appointment
function editAppointment(appointmentId) {
    // Implementation will be added
    console.log('Edit appointment:', appointmentId);
}

// Function to cancel appointment
async function cancelAppointment(appointmentId) {
    if (!confirm('Are you sure you want to cancel this appointment?')) {
        return;
    }

    try {
        const response = await fetch(`/api/appointments/${appointmentId}/cancel/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });

        if (response.ok) {
            // Reload appointments to reflect the change
            loadAppointments();
        } else {
            throw new Error('Failed to cancel appointment');
        }
    } catch (error) {
        console.error('Error canceling appointment:', error);
        alert('Failed to cancel appointment. Please try again.');
    }
}
