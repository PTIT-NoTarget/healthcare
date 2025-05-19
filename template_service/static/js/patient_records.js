document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const searchInput = document.getElementById('searchInput');
    const filterStatus = document.getElementById('filterStatus');
    const sortBy = document.getElementById('sortBy');
    const patientList = document.getElementById('patientList');
    const savePatientBtn = document.getElementById('savePatient');

    // Load initial data
    loadPatients();

    // Event listeners
    searchInput.addEventListener('input', debounce(filterPatients, 300));
    filterStatus.addEventListener('change', filterPatients);
    sortBy.addEventListener('change', filterPatients);
    savePatientBtn.addEventListener('click', saveNewPatient);

    // Function to load patients
    async function loadPatients() {
        try {
            const response = await fetch('/api/patients/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const patients = await response.json();
            displayPatients(patients);
        } catch (error) {
            console.error('Error loading patients:', error);
            showAlert('Error loading patients. Please try again.', 'danger');
        }
    }

    // Function to display patients
    function displayPatients(patients) {
        patientList.innerHTML = patients.map(patient => `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="card-title mb-0">${patient.firstName} ${patient.lastName}</h5>
                            <span class="badge bg-${patient.status === 'active' ? 'success' : 'secondary'}">${patient.status}</span>
                        </div>
                        <p class="card-text">
                            <small class="text-muted">ID: ${patient.id}</small><br>
                            <i class="fas fa-birthday-cake"></i> ${formatDate(patient.dateOfBirth)}<br>
                            <i class="fas fa-phone"></i> ${patient.phone || 'N/A'}<br>
                            <i class="fas fa-envelope"></i> ${patient.email || 'N/A'}
                        </p>
                        <div class="d-flex justify-content-end gap-2 mt-3">
                            <button class="btn btn-sm btn-outline-primary" onclick="viewPatientDetails('${patient.id}')">
                                <i class="fas fa-eye"></i> View
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="editPatient('${patient.id}')">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Function to save new patient
    async function saveNewPatient() {
        const formData = {
            firstName: document.getElementById('firstName').value,
            lastName: document.getElementById('lastName').value,
            dateOfBirth: document.getElementById('dateOfBirth').value,
            gender: document.getElementById('gender').value,
            phone: document.getElementById('phone').value,
            email: document.getElementById('email').value,
            address: document.getElementById('address').value,
            emergencyContactName: document.getElementById('emergencyContactName').value,
            emergencyContactPhone: document.getElementById('emergencyContactPhone').value,
            status: 'active'
        };

        try {
            const response = await fetch('/api/patients/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('newPatientModal'));
                modal.hide();
                document.getElementById('newPatientForm').reset();
                loadPatients();
                showAlert('Patient added successfully!', 'success');
            } else {
                throw new Error('Failed to add patient');
            }
        } catch (error) {
            console.error('Error saving patient:', error);
            showAlert('Error saving patient. Please try again.', 'danger');
        }
    }

    // Function to view patient details
    window.viewPatientDetails = async function(patientId) {
        try {
            const response = await fetch(`/api/patients/${patientId}/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const patient = await response.json();
            displayPatientDetails(patient);
            const modal = new bootstrap.Modal(document.getElementById('patientDetailsModal'));
            modal.show();
        } catch (error) {
            console.error('Error loading patient details:', error);
            showAlert('Error loading patient details. Please try again.', 'danger');
        }
    }

    // Function to display patient details
    function displayPatientDetails(patient) {
        const basicInfo = document.getElementById('basicInfo');
        basicInfo.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Name:</strong> ${patient.firstName} ${patient.lastName}</p>
                    <p><strong>Date of Birth:</strong> ${formatDate(patient.dateOfBirth)}</p>
                    <p><strong>Gender:</strong> ${patient.gender}</p>
                    <p><strong>Status:</strong> ${patient.status}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Phone:</strong> ${patient.phone || 'N/A'}</p>
                    <p><strong>Email:</strong> ${patient.email || 'N/A'}</p>
                    <p><strong>Address:</strong> ${patient.address || 'N/A'}</p>
                </div>
                <div class="col-12">
                    <h6 class="mt-3">Emergency Contact</h6>
                    <p><strong>Name:</strong> ${patient.emergencyContactName || 'N/A'}</p>
                    <p><strong>Phone:</strong> ${patient.emergencyContactPhone || 'N/A'}</p>
                </div>
            </div>
        `;
        // Load other tabs data here (medical history, appointments, prescriptions)
    }

    // Helper function to format date
    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }

    // Helper function to show alerts
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.card'));
        setTimeout(() => alertDiv.remove(), 5000);
    }

    // Helper function to debounce search input
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Function to filter patients
    function filterPatients() {
        // Implementation will be added based on backend API
        loadPatients();
    }
});
