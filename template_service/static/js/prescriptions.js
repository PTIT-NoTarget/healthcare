// Constants
const API_BASE_URL = '/api';

// Utility functions
const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
};

// Helper function for status badge color
function getStatusBadgeClass(status) {
    if (!status) return 'secondary';
    const statusClasses = {
        'active': 'success',
        'completed': 'info',
        'canceled': 'danger'
    };
    return statusClasses[status.toLowerCase()] || 'secondary';
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

    // Function to load patients
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

    // Function to load medications
    async function loadMedications() {
        try {
            const response = await fetch(`${API_BASE_URL}/medicines/`);
            const medicines = await response.json();
            
            if (!medicines || !Array.isArray(medicines)) {
                console.error('Invalid medicines data:', medicines);
                return;
            }
            
            const medicationSelect = document.getElementById('medicationSelect');
            medicationSelect.innerHTML = '<option value="">Select Medication</option>';
    
            console.log('Loaded medicines:', medicines);
            medicines.forEach(medicine => {
                // Check if medicine has a valid ID field
                if (!medicine.id) {
                    console.warn('Medicine missing ID:', medicine);
                    return;
                }
                const option = new Option(`${medicine.name}`, medicine.id);
                medicationSelect.add(option);
            });
        } catch (error) {
            console.error('Error loading medicines:', error);
            showErrorAlert('Failed to load medicines list');
        }
    }

    // Function to load prescriptions
    async function loadPrescriptions() {
        try {
            // Show loading indicator
            prescriptionsList.innerHTML = '<div class="col-12 text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';
            
            const response = await fetch(`${API_BASE_URL}/prescriptions/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error ${response.status}`);
            }
            
            const prescriptions = await response.json();
            console.log('Loaded prescriptions:', prescriptions);
            
            if (!prescriptions || !Array.isArray(prescriptions)) {
                throw new Error('Invalid prescription data format');
            }
            
            displayPrescriptions(prescriptions);
        } catch (error) {
            console.error('Error loading prescriptions:', error);
            prescriptionsList.innerHTML = '<div class="col-12 alert alert-danger">Error loading prescriptions. Please try again.</div>';
        }
    }

    // Function to display prescriptions
    function displayPrescriptions(prescriptions) {
        if (!prescriptions || prescriptions.length === 0) {
            prescriptionsList.innerHTML = '<div class="col-12 text-center">No prescriptions found</div>';
            return;
        }
        
        prescriptionsList.innerHTML = prescriptions.map(prescription => {
            // Use prescription_id instead of id since id is null
            const id = prescription.prescription_id || 'Unknown';
            const status = prescription.status || 'Unknown';
            const patientName = prescription.patient_name || 'Unknown Patient';
            const doctorName = prescription.doctor_name || 'Unknown Doctor';
            const createdAt = prescription.date_prescribed || prescription.created_at || null;
            const medications = prescription.medication_details || [];
            
            return `
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5 class="card-title mb-0">Prescription #${id}</h5>
                                <span class="badge bg-${getStatusBadgeClass(status)}">${status}</span>
                            </div>
                            <p class="card-text">
                                <strong>Patient:</strong> ${patientName}<br>
                                <strong>Doctor:</strong> ${doctorName}<br>
                                <strong>Date:</strong> ${formatDate(createdAt)}<br>
                                <strong>Medications:</strong> ${medications.length} items
                            </p>
                            <div class="d-flex justify-content-end gap-2">
                                <button class="btn btn-sm btn-outline-primary" onclick="viewPrescriptionDetails('${id}')">
                                    <i class="fas fa-eye"></i> View
                                </button>
                                <button class="btn btn-sm btn-outline-info" onclick="printPrescription('${id}')">
                                    <i class="fas fa-print"></i> Print
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
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
            const response = await fetch(`${API_BASE_URL}/prescriptions/`, {
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
                const error = await response.json();
                throw new Error(error.message || 'Failed to create prescription');
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

        // Repopulate medication options
        const medicationSelect = medicationItem.querySelector('.medication-select');
        medicationSelect.innerHTML = '';
        const originalSelect = document.querySelector('.medication-select');
        Array.from(originalSelect.options).forEach(option => {
            medicationSelect.add(option.cloneNode(true));
        });

        const removeBtn = medicationItem.querySelector('.remove-medication');
        removeBtn.addEventListener('click', () => medicationItem.remove());

        document.getElementById('medicationsList').appendChild(medicationItem);
    }

    // Function to filter prescriptions
    function filterPrescriptions() {
        const searchTerm = searchInput.value.toLowerCase();
        const status = statusFilter.value;
        const date = dateFilter.value;

        // Build query parameters
        const filters = {};
        
        if (status && status !== 'all') {
            filters.status = status;
        }
        
        if (date && date !== 'all') {
            const today = new Date();
            if (date === 'today') {
                filters.date = today.toISOString().split('T')[0];
            } else if (date === 'week') {
                const weekAgo = new Date(today);
                weekAgo.setDate(today.getDate() - 7);
                filters.start_date = weekAgo.toISOString().split('T')[0];
                filters.end_date = today.toISOString().split('T')[0];
            } else if (date === 'month') {
                const monthAgo = new Date(today);
                monthAgo.setMonth(today.getMonth() - 1);
                filters.start_date = monthAgo.toISOString().split('T')[0];
                filters.end_date = today.toISOString().split('T')[0];
            }
        }
        
        if (searchTerm) {
            filters.search = searchTerm;
        }
        
        // Convert filters to query string
        const queryString = new URLSearchParams(filters).toString();
        
        // Fetch filtered prescriptions
        fetch(`${API_BASE_URL}/prescriptions/?${queryString}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        })
        .then(response => response.json())
        .then(prescriptions => {
            displayPrescriptions(prescriptions);
        })
        .catch(error => {
            console.error('Error filtering prescriptions:', error);
            showAlert('Error filtering prescriptions', 'danger');
        });
    }
});

// Global functions for prescription actions
window.viewPrescriptionDetails = async function(prescriptionId) {
    try {
        const response = await fetch(`${API_BASE_URL}/prescriptions/${prescriptionId}/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        const prescription = await response.json();

        // Map prescription fields to match the API response
        const id = prescription.prescription_id || 'Unknown';
        const status = prescription.status || 'Unknown';
        const patientName = prescription.patient_name || 'Unknown Patient';
        const doctorName = prescription.doctor_name || 'Unknown Doctor';
        const createdAt = prescription.date_prescribed || prescription.created_at || null;
        const diagnosis = prescription.diagnosis || 'No diagnosis provided';
        const instructions = prescription.notes || 'No instructions provided';
        const medications = prescription.medication_details || [];

        const detailsDiv = document.getElementById('prescriptionDetails');
        detailsDiv.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Prescription ID:</strong> #${id}</p>
                    <p><strong>Date:</strong> ${formatDate(createdAt)}</p>
                    <p><strong>Status:</strong> <span class="badge bg-${getStatusBadgeClass(status)}">${status}</span></p>
                </div>
                <div class="col-md-6">
                    <p><strong>Patient:</strong> ${patientName}</p>
                    <p><strong>Doctor:</strong> ${doctorName}</p>
                </div>
                <div class="col-12">
                    <hr>
                    <h6>Diagnosis</h6>
                    <p>${diagnosis}</p>
                    
                    <h6>Medications</h6>
                    <ul class="list-group mb-3">
                        ${medications.map(med => {
                            // Map medication fields to match the API response
                            const name = med.medicine_name || 'Unknown Medication';
                            const dosage = med.dosage || 'Not specified';
                            const quantity = med.quantity || '1';
                            const duration = med.duration || 'Not specified';
                            const frequency = med.frequency || 'Not specified';
                            const medicineInstructions = med.instructions || 'Not specified';
                            
                            return `
                                <li class="list-group-item">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            <h6 class="mb-0">${name}</h6>
                                            <small class="text-muted">Dosage: ${dosage}</small>
                                            <small class="d-block text-muted">Frequency: ${frequency}</small>
                                            <small class="d-block text-muted">Instructions: ${medicineInstructions}</small>
                                        </div>
                                        <div class="text-end">
                                            <small class="d-block">Duration: ${duration}</small>
                                        </div>
                                    </div>
                                </li>
                            `;
                        }).join('')}
                    </ul>
                    
                    <h6>Instructions</h6>
                    <p>${instructions}</p>
                </div>
            </div>
        `;

        const modal = new bootstrap.Modal(document.getElementById('prescriptionDetailsModal'));
        modal.show();
        
        // Setup print button
        document.getElementById('printPrescription').onclick = function() {
            printPrescription(id);
        };
    } catch (error) {
        console.error('Error loading prescription details:', error);
        showAlert('Error loading prescription details. Please try again.', 'danger');
    }
};

window.printPrescription = function(prescriptionId) {
    window.open(`${API_BASE_URL}/prescriptions/${prescriptionId}/print/`, '_blank');
};

// Helper function for alerts since it's missing in the code
function showAlert(message, type) {
    const alertContainer = document.querySelector('.alert-container') || document.createElement('div');
    if (!document.querySelector('.alert-container')) {
        alertContainer.className = 'alert-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(alertContainer);
    }
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// For backwards compatibility
function showErrorAlert(message) {
    showAlert(message, 'danger');
}
