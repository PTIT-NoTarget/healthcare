// Constants
const API_BASE_URL = '/api';

// Utility functions
const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
};

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
    const dateFilter = document.getElementById('dateFilter');
    const prescriptionsList = document.getElementById('prescriptionsList');
    const prescriptionForm = document.getElementById('prescriptionForm');
    const savePrescriptionBtn = document.getElementById('savePrescription');
    const addMedicationBtn = document.getElementById('addMedication');
    
    // Store all prescriptions for client-side filtering
    let allPrescriptions = [];

    // Load initial data
    loadDoctors();
    loadPatients();
    loadMedications();
    loadPrescriptions();

    // Event listeners
    searchInput.addEventListener('input', debounce(filterPrescriptions, 300));
    dateFilter.addEventListener('change', filterPrescriptions);
    savePrescriptionBtn.addEventListener('click', savePrescription);
    addMedicationBtn.addEventListener('click', addMedicationField);
    
    // Add event listener for initial medication remove button
    document.querySelector('.remove-medication').addEventListener('click', function(e) {
        // Don't remove if it's the only medication item
        if (document.querySelectorAll('.medication-item').length > 1) {
            e.target.closest('.medication-item').remove();
        } else {
            showAlert('At least one medication is required', 'warning');
        }
    });

    // Function to load doctors
    async function loadDoctors() {
        try {
            const response = await fetch(`${API_BASE_URL}/doctors/`);
            const doctors = await response.json();
    
            const doctorSelect = document.getElementById('doctorSelect');
            if (!doctorSelect) return;
            
            doctorSelect.innerHTML = '<option value="">Select Doctor</option>';
    
            doctors.forEach(doctor => {
                const option = new Option(`Dr. ${doctor.first_name} ${doctor.last_name}`, doctor.user_id);
                doctorSelect.add(option);
            });
        } catch (error) {
            console.error('Error loading doctors:', error);
            showAlert('Failed to load doctors list', 'danger');
        }
    }

    // Function to load patients
    async function loadPatients() {
        try {
            const response = await fetch(`${API_BASE_URL}/patients/`);
            const patients = await response.json();
    
            const patientSelect = document.getElementById('patientSelect');
            if (!patientSelect) return;
            
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
            showAlert('Failed to load patients list', 'danger');
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
            
            // Get all medication selects
            const medicationSelects = document.querySelectorAll('.medication-select');
            
            medicationSelects.forEach(select => {
                select.innerHTML = '<option value="">Select Medication</option>';
                
                medicines.forEach(medicine => {
                    // Check if medicine has a valid ID field
                    if (!medicine.id) {
                        console.warn('Medicine missing ID:', medicine);
                        return;
                    }
                    const option = new Option(`${medicine.name} (${medicine.strength})`, medicine.id);
                    select.add(option);
                });
            });
            
            console.log('Loaded medicines:', medicines);
        } catch (error) {
            console.error('Error loading medicines:', error);
            showAlert('Failed to load medicines list', 'danger');
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
            
            // Store all prescriptions for client-side filtering
            allPrescriptions = prescriptions;
            
            // Display all prescriptions initially
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
            const id = prescription.id || prescription.prescription_id || 'Unknown';
            const patientName = prescription.patient_name || 'Unknown Patient';
            const doctorName = prescription.doctor_name || 'Unknown Doctor';
            const createdAt = prescription.date_prescribed || prescription.created_at || null;
            const medications = prescription.medication_details || [];
            
            return `
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <div class="mb-3">
                                <h5 class="card-title mb-0">Prescription #${id}</h5>
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
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Function to save prescription
    async function savePrescription() {
        try {
            const medications = [];
            const medicationItems = document.querySelectorAll('.medication-item');
            
            // Validate form
            const patientId = document.getElementById('patientSelect').value;
            const doctorId = document.getElementById('doctorSelect').value;
            const diagnosis = document.getElementById('diagnosis').value;
            const instructions = document.getElementById('instructions').value;
            
            if (!patientId || !doctorId || !diagnosis || !instructions) {
                showAlert('Please fill in all required fields', 'warning');
                return;
            }

            // Check each medication item
            let isValid = true;
            medicationItems.forEach((item, index) => {
                const medicineId = item.querySelector('.medication-select').value;
                const frequency = item.querySelector('input[placeholder="Frequency"]').value;
                const dosage = item.querySelector('input[placeholder="Dosage"]').value;
                const duration = item.querySelector('input[placeholder="Duration"]').value;

                if (!medicineId || !frequency || !dosage || !duration) {
                    showAlert(`Please complete all fields for medication #${index + 1}`, 'warning');
                    isValid = false;
                    return;
                }

                medications.push({
                    medicine_id: medicineId,
                    frequency: frequency,
                    dosage: dosage,
                    duration: duration,
                    instructions: `Take ${dosage} ${frequency} for ${duration}`
                });
            });
            
            if (!isValid) return;
            if (medications.length === 0) {
                showAlert('Please add at least one medication', 'warning');
                return;
            }

            // Construct the prescription data
            const prescriptionData = {
                patient_id: patientId,
                doctor_id: doctorId,
                diagnosis: diagnosis,
                notes: instructions,
                medications: medications
            };
            
            console.log('Saving prescription:', prescriptionData);

            // Show loading state
            savePrescriptionBtn.disabled = true;
            savePrescriptionBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';

            const response = await fetch(`${API_BASE_URL}/prescriptions/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(prescriptionData)
            });

            // Reset button state
            savePrescriptionBtn.disabled = false;
            savePrescriptionBtn.innerHTML = '<i class="fas fa-save"></i> Create Prescription';

            if (response.ok) {
                const newPrescription = await response.json();
                console.log('Created prescription:', newPrescription);
                
                // Close modal and reset form
                const modal = bootstrap.Modal.getInstance(document.getElementById('newPrescriptionModal'));
                modal.hide();
                prescriptionForm.reset();
                
                // Reset medication items
                const medicationsList = document.getElementById('medicationsList');
                const firstItem = medicationItems[0].cloneNode(true);
                
                // Clear all values in the first item
                firstItem.querySelectorAll('select, input').forEach(el => el.value = '');
                
                // Add event listener to the remove button
                firstItem.querySelector('.remove-medication').addEventListener('click', function() {
                    showAlert('At least one medication is required', 'warning');
                });
                
                medicationsList.innerHTML = '';
                medicationsList.appendChild(firstItem);
                
                // Reload medications in the first item
                loadMedications();
                
                // Reload prescriptions list
                await loadPrescriptions();
                
                showAlert('Prescription created successfully!', 'success');
            } else {
                const error = await response.json();
                throw new Error(error.message || error.detail || 'Failed to create prescription');
            }
        } catch (error) {
            console.error('Error creating prescription:', error);
            showAlert(`Error creating prescription: ${error.message}`, 'danger');
        }
    }

    // Function to add medication field
    function addMedicationField() {
        // Clone the first medication item
        const firstMedicationItem = document.querySelector('.medication-item');
        const medicationItem = firstMedicationItem.cloneNode(true);
        
        // Clear all inputs
        medicationItem.querySelectorAll('input, select').forEach(input => input.value = '');

        // Add event listener to remove button
        const removeBtn = medicationItem.querySelector('.remove-medication');
        removeBtn.addEventListener('click', function() {
            medicationItem.remove();
        });

        // Add the new medication item to the list
        document.getElementById('medicationsList').appendChild(medicationItem);
        
        // Load medications in the new item
        const medicationSelect = medicationItem.querySelector('.medication-select');
        populateMedicationSelect(medicationSelect);
    }
    
    // Function to populate a medication select dropdown
    async function populateMedicationSelect(select) {
        try {
            const response = await fetch(`${API_BASE_URL}/medicines/`);
            const medicines = await response.json();
            
            select.innerHTML = '<option value="">Select Medication</option>';
            
            medicines.forEach(medicine => {
                if (!medicine.id) return;
                const option = new Option(`${medicine.name} (${medicine.strength})`, medicine.id);
                select.add(option);
            });
        } catch (error) {
            console.error('Error loading medicines for select:', error);
        }
    }

    // Function to filter prescriptions
    function filterPrescriptions() {
        const searchTerm = searchInput.value.toLowerCase();
        const date = dateFilter.value;
        
        // Apply client-side filtering to allPrescriptions
        const filteredPrescriptions = allPrescriptions.filter(prescription => {
            // Apply search filter
            const prescriptionId = prescription.id || prescription.prescription_id || '';
            const patientName = prescription.patient_name || '';
            const doctorName = prescription.doctor_name || '';
            const diagnosis = prescription.diagnosis || '';
            
            const matchesSearch = !searchTerm || 
                prescriptionId.toLowerCase().includes(searchTerm) ||
                patientName.toLowerCase().includes(searchTerm) ||
                doctorName.toLowerCase().includes(searchTerm) ||
                diagnosis.toLowerCase().includes(searchTerm);
            
            if (!matchesSearch) return false;
            
            // Apply date filter
            if (date && date !== 'all') {
                const prescriptionDate = new Date(prescription.date_prescribed || prescription.created_at);
                const today = new Date();
                today.setHours(0, 0, 0, 0);
                
                if (date === 'today') {
                    const tomorrow = new Date(today);
                    tomorrow.setDate(tomorrow.getDate() + 1);
                    return prescriptionDate >= today && prescriptionDate < tomorrow;
                } else if (date === 'week') {
                    const weekAgo = new Date(today);
                    weekAgo.setDate(today.getDate() - 7);
                    return prescriptionDate >= weekAgo;
                } else if (date === 'month') {
                    const monthAgo = new Date(today);
                    monthAgo.setMonth(today.getMonth() - 1);
                    return prescriptionDate >= monthAgo;
                }
            }
            
            return true;
        });
        
        displayPrescriptions(filteredPrescriptions);
    }
});

// Global functions for prescription actions
window.viewPrescriptionDetails = async function(prescriptionId) {
    try {
        // Use the prescription ID directly for the API call
        const response = await fetch(`${API_BASE_URL}/prescriptions/${prescriptionId}/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`Failed to fetch prescription details: ${response.status}`);
        }
        
        const prescription = await response.json();
        console.log('Prescription details:', prescription);

        // Map prescription fields to match the API response
        const id = prescription.id || prescription.prescription_id || 'Unknown';
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
    } catch (error) {
        console.error('Error loading prescription details:', error);
        showAlert('Error loading prescription details. Please try again.', 'danger');
    }
};

// Helper function for alerts
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
