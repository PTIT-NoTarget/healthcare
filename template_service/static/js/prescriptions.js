document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const dateFilter = document.getElementById('dateFilter');
    const prescriptionsList = document.getElementById('prescriptionsList');
    const prescriptionForm = document.getElementById('prescriptionForm');
    const savePrescriptionBtn = document.getElementById('savePrescription');
    const addMedicationBtn = document.getElementById('addMedication');

    // Load initial data
    loadDoctors();
    loadPatients();
    loadMedications();
    loadPrescriptions();

    // Event listeners
    searchInput.addEventListener('input', debounce(filterPrescriptions, 300));
    statusFilter.addEventListener('change', filterPrescriptions);
    dateFilter.addEventListener('change', filterPrescriptions);
    savePrescriptionBtn.addEventListener('click', savePrescription);
    addMedicationBtn.addEventListener('click', addMedicationField);

    // Function to load doctors
    async function loadDoctors() {
        try {
            const response = await fetch('/api/doctors/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const doctors = await response.json();
            const doctorSelect = document.getElementById('doctorSelect');
            doctors.forEach(doctor => {
                const option = document.createElement('option');
                option.value = doctor.id;
                option.textContent = `Dr. ${doctor.firstName} ${doctor.lastName}`;
                doctorSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading doctors:', error);
            showAlert('Error loading doctors', 'danger');
        }
    }

    // Function to load patients
    async function loadPatients() {
        try {
            const response = await fetch('/api/patients/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const patients = await response.json();
            const patientSelect = document.getElementById('patientSelect');
            patients.forEach(patient => {
                const option = document.createElement('option');
                option.value = patient.id;
                option.textContent = `${patient.firstName} ${patient.lastName}`;
                patientSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading patients:', error);
            showAlert('Error loading patients', 'danger');
        }
    }

    // Function to load medications
    async function loadMedications() {
        try {
            const response = await fetch('/api/medications/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const medications = await response.json();
            const medicationSelects = document.getElementsByClassName('medication-select');
            Array.from(medicationSelects).forEach(select => {
                medications.forEach(medication => {
                    const option = document.createElement('option');
                    option.value = medication.id;
                    option.textContent = medication.name;
                    select.appendChild(option);
                });
            });
        } catch (error) {
            console.error('Error loading medications:', error);
            showAlert('Error loading medications', 'danger');
        }
    }

    // Function to load prescriptions
    async function loadPrescriptions() {
        try {
            const response = await fetch('/api/prescriptions/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const prescriptions = await response.json();
            displayPrescriptions(prescriptions);
        } catch (error) {
            console.error('Error loading prescriptions:', error);
            showAlert('Error loading prescriptions', 'danger');
        }
    }

    // Function to display prescriptions
    function displayPrescriptions(prescriptions) {
        prescriptionsList.innerHTML = prescriptions.map(prescription => `
            <div class="col-md-6 mb-4">
                <div class="card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="card-title mb-0">Prescription #${prescription.id}</h5>
                            <span class="badge bg-${getStatusBadgeClass(prescription.status)}">${prescription.status}</span>
                        </div>
                        <p class="card-text">
                            <strong>Patient:</strong> ${prescription.patientName}<br>
                            <strong>Doctor:</strong> Dr. ${prescription.doctorName}<br>
                            <strong>Date:</strong> ${formatDate(prescription.createdAt)}<br>
                            <strong>Medications:</strong> ${prescription.medications.length} items
                        </p>
                        <div class="d-flex justify-content-end gap-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="viewPrescriptionDetails('${prescription.id}')">
                                <i class="fas fa-eye"></i> View
                            </button>
                            <button class="btn btn-sm btn-outline-info" onclick="printPrescription('${prescription.id}')">
                                <i class="fas fa-print"></i> Print
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    // Function to save prescription
    async function savePrescription() {
        const medications = [];
        const medicationItems = document.getElementsByClassName('medication-item');

        Array.from(medicationItems).forEach(item => {
            const medicationId = item.querySelector('.medication-select').value;
            const quantity = item.querySelector('input[placeholder="Quantity"]').value;
            const dosage = item.querySelector('input[placeholder="Dosage"]').value;
            const duration = item.querySelector('input[placeholder="Duration"]').value;

            medications.push({
                medicationId,
                quantity: parseInt(quantity),
                dosage,
                duration
            });
        });

        const prescriptionData = {
            patientId: document.getElementById('patientSelect').value,
            doctorId: document.getElementById('doctorSelect').value,
            diagnosis: document.getElementById('diagnosis').value,
            instructions: document.getElementById('instructions').value,
            medications
        };

        try {
            const response = await fetch('/api/prescriptions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(prescriptionData)
            });

            if (response.ok) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('newPrescriptionModal'));
                modal.hide();
                prescriptionForm.reset();
                loadPrescriptions();
                showAlert('Prescription created successfully!', 'success');
            } else {
                throw new Error('Failed to create prescription');
            }
        } catch (error) {
            console.error('Error creating prescription:', error);
            showAlert('Error creating prescription. Please try again.', 'danger');
        }
    }

    // Function to add medication field
    function addMedicationField() {
        const medicationItem = document.querySelector('.medication-item').cloneNode(true);
        medicationItem.querySelectorAll('input').forEach(input => input.value = '');
        medicationItem.querySelector('select').value = '';

        const removeBtn = medicationItem.querySelector('.remove-medication');
        removeBtn.addEventListener('click', () => medicationItem.remove());

        document.getElementById('medicationsList').appendChild(medicationItem);
    }

    // Function to filter prescriptions
    function filterPrescriptions() {
        const searchTerm = searchInput.value.toLowerCase();
        const status = statusFilter.value;
        const date = dateFilter.value;

        loadPrescriptions(); // In real implementation, these filters would be passed to the API
    }

    // Helper function for status badge color
    function getStatusBadgeClass(status) {
        const statusClasses = {
            'active': 'success',
            'completed': 'info',
            'canceled': 'danger'
        };
        return statusClasses[status.toLowerCase()] || 'secondary';
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
});

// Global functions for prescription actions
window.viewPrescriptionDetails = async function(prescriptionId) {
    try {
        const response = await fetch(`/api/prescriptions/${prescriptionId}/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        const prescription = await response.json();

        const detailsDiv = document.getElementById('prescriptionDetails');
        detailsDiv.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Prescription ID:</strong> #${prescription.id}</p>
                    <p><strong>Date:</strong> ${formatDate(prescription.createdAt)}</p>
                    <p><strong>Status:</strong> <span class="badge bg-${getStatusBadgeClass(prescription.status)}">${prescription.status}</span></p>
                </div>
                <div class="col-md-6">
                    <p><strong>Patient:</strong> ${prescription.patientName}</p>
                    <p><strong>Doctor:</strong> Dr. ${prescription.doctorName}</p>
                </div>
                <div class="col-12">
                    <hr>
                    <h6>Diagnosis</h6>
                    <p>${prescription.diagnosis}</p>
                    
                    <h6>Medications</h6>
                    <ul class="list-group mb-3">
                        ${prescription.medications.map(med => `
                            <li class="list-group-item">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 class="mb-0">${med.name}</h6>
                                        <small class="text-muted">Dosage: ${med.dosage}</small>
                                    </div>
                                    <div class="text-end">
                                        <small class="d-block">Quantity: ${med.quantity}</small>
                                        <small class="d-block">Duration: ${med.duration}</small>
                                    </div>
                                </div>
                            </li>
                        `).join('')}
                    </ul>
                    
                    <h6>Instructions</h6>
                    <p>${prescription.instructions}</p>
                </div>
            </div>
        `;

        const modal = new bootstrap.Modal(document.getElementById('prescriptionDetailsModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading prescription details:', error);
        showAlert('Error loading prescription details. Please try again.', 'danger');
    }
};

window.printPrescription = function(prescriptionId) {
    window.open(`/api/prescriptions/${prescriptionId}/print/`, '_blank');
};
