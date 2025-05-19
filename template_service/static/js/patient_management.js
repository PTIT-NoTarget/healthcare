document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const genderFilter = document.getElementById('genderFilter');
    const patientsTable = document.getElementById('patientsTable').getElementsByTagName('tbody')[0];
    const patientForm = document.getElementById('patientForm');
    const savePatientBtn = document.getElementById('savePatient');
    const editPatientBtn = document.getElementById('editPatient');
    let currentPage = 1;
    let totalPages = 1;

    // Load initial data
    loadPatients();
    loadStatistics();

    // Event listeners
    searchInput.addEventListener('input', debounce(filterPatients, 300));
    statusFilter.addEventListener('change', filterPatients);
    genderFilter.addEventListener('change', filterPatients);
    savePatientBtn.addEventListener('click', savePatient);
    editPatientBtn.addEventListener('click', enablePatientEdit);

    // Function to load patients
    async function loadPatients(page = 1) {
        try {
            const response = await fetch(`/api/patients/?page=${page}`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const data = await response.json();
            displayPatients(data.results);
            updatePagination(data.total_pages, page);
        } catch (error) {
            console.error('Error loading patients:', error);
            showAlert('Error loading patients. Please try again.', 'danger');
        }
    }

    // Function to load statistics
    async function loadStatistics() {
        try {
            const response = await fetch('/api/patients/statistics/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const stats = await response.json();
            updateStatistics(stats);
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    // Function to display patients
    function displayPatients(patients) {
        patientsTable.innerHTML = patients.map(patient => `
            <tr>
                <td>${patient.id}</td>
                <td>${patient.firstName} ${patient.lastName}</td>
                <td>${calculateAge(patient.dateOfBirth)} / ${patient.gender}</td>
                <td>
                    <div>${patient.phone}</div>
                    <small class="text-muted">${patient.email || 'N/A'}</small>
                </td>
                <td>${patient.lastVisit ? formatDate(patient.lastVisit) : 'Never'}</td>
                <td>${getStatusBadge(patient.status)}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="viewPatientDetails(${patient.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="createAppointment(${patient.id})">
                            <i class="fas fa-calendar-plus"></i>
                        </button>
                        <button class="btn btn-outline-info" onclick="createPrescription(${patient.id})">
                            <i class="fas fa-prescription"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // Function to update statistics
    function updateStatistics(stats) {
        document.getElementById('totalPatients').textContent = stats.totalPatients;
        document.getElementById('activePatients').textContent = stats.activePatients;
        document.getElementById('todayAppointments').textContent = stats.todayAppointments;
        document.getElementById('pendingReports').textContent = stats.pendingReports;
    }

    // Function to save new patient
    async function savePatient() {
        const formData = {
            firstName: document.getElementById('firstName').value,
            lastName: document.getElementById('lastName').value,
            dateOfBirth: document.getElementById('dateOfBirth').value,
            gender: document.getElementById('gender').value,
            bloodGroup: document.getElementById('bloodGroup').value,
            phone: document.getElementById('phone').value,
            email: document.getElementById('email').value,
            address: document.getElementById('address').value,
            emergencyContact: {
                name: document.getElementById('emergencyName').value,
                relationship: document.getElementById('emergencyRelation').value,
                phone: document.getElementById('emergencyPhone').value
            },
            medicalInfo: {
                allergies: document.getElementById('allergies').value,
                medications: document.getElementById('medications').value,
                medicalHistory: document.getElementById('medicalHistory').value
            },
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
                const modal = bootstrap.Modal.getInstance(document.getElementById('addPatientModal'));
                modal.hide();
                patientForm.reset();
                loadPatients();
                loadStatistics();
                showAlert('Patient added successfully!', 'success');
            } else {
                throw new Error('Failed to add patient');
            }
        } catch (error) {
            console.error('Error saving patient:', error);
            showAlert('Error saving patient. Please try again.', 'danger');
        }
    }

    // Function to update pagination
    function updatePagination(total, current) {
        totalPages = total;
        currentPage = current;
        const pagination = document.getElementById('pagination');
        let pages = '';

        // Previous button
        pages += `
            <li class="page-item ${current === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="changePage(${current - 1})">Previous</a>
            </li>
        `;

        // Page numbers
        for (let i = 1; i <= total; i++) {
            pages += `
                <li class="page-item ${i === current ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
                </li>
            `;
        }

        // Next button
        pages += `
            <li class="page-item ${current === total ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="changePage(${current + 1})">Next</a>
            </li>
        `;

        pagination.innerHTML = pages;
    }

    // Function to filter patients
    function filterPatients() {
        const searchTerm = searchInput.value.toLowerCase();
        const status = statusFilter.value;
        const gender = genderFilter.value;

        loadPatients(1); // Reset to first page with filters
    }

    // Helper function to calculate age
    function calculateAge(dateOfBirth) {
        const today = new Date();
        const birthDate = new Date(dateOfBirth);
        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age;
    }

    // Helper function for status badge
    function getStatusBadge(status) {
        const badges = {
            'active': 'success',
            'inactive': 'secondary'
        };
        return `<span class="badge bg-${badges[status] || 'secondary'}">${status}</span>`;
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

    // Expose necessary functions to window object
    window.changePage = function(page) {
        if (page > 0 && page <= totalPages) {
            loadPatients(page);
        }
    };
});

// Global functions for patient actions
window.viewPatientDetails = async function(patientId) {
    try {
        const response = await fetch(`/api/patients/${patientId}/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        const patient = await response.json();
        displayPatientDetails(patient);
        const modal = new bootstrap.Modal(document.getElementById('viewPatientModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading patient details:', error);
        showAlert('Error loading patient details. Please try again.', 'danger');
    }
};

window.createAppointment = function(patientId) {
    // Redirect to appointments page with patient pre-selected
    window.location.href = `/appointments?patient=${patientId}`;
};

window.createPrescription = function(patientId) {
    // Redirect to prescriptions page with patient pre-selected
    window.location.href = `/prescriptions?patient=${patientId}`;
};

// Function to display patient details in modal
function displayPatientDetails(patient) {
    const overview = document.getElementById('overview');
    overview.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Personal Information</h6>
                <p><strong>Name:</strong> ${patient.firstName} ${patient.lastName}</p>
                <p><strong>Date of Birth:</strong> ${formatDate(patient.dateOfBirth)} (${calculateAge(patient.dateOfBirth)} years)</p>
                <p><strong>Gender:</strong> ${patient.gender}</p>
                <p><strong>Blood Group:</strong> ${patient.bloodGroup || 'N/A'}</p>
            </div>
            <div class="col-md-6">
                <h6>Contact Information</h6>
                <p><strong>Phone:</strong> ${patient.phone}</p>
                <p><strong>Email:</strong> ${patient.email || 'N/A'}</p>
                <p><strong>Address:</strong> ${patient.address}</p>
            </div>
            <div class="col-12"><hr></div>
            <div class="col-md-6">
                <h6>Emergency Contact</h6>
                <p><strong>Name:</strong> ${patient.emergencyContact.name}</p>
                <p><strong>Relationship:</strong> ${patient.emergencyContact.relationship}</p>
                <p><strong>Phone:</strong> ${patient.emergencyContact.phone}</p>
            </div>
            <div class="col-md-6">
                <h6>Medical Information</h6>
                <p><strong>Allergies:</strong> ${patient.medicalInfo.allergies || 'None'}</p>
                <p><strong>Current Medications:</strong> ${patient.medicalInfo.medications || 'None'}</p>
                <p><strong>Medical History:</strong> ${patient.medicalInfo.medicalHistory || 'None'}</p>
            </div>
        </div>
    `;

    // Load other tabs data
    loadPatientAppointments(patient.id);
    loadPatientMedicalRecords(patient.id);
    loadPatientPrescriptions(patient.id);
    loadPatientLabResults(patient.id);
}

// Functions to load patient-related data for tabs
async function loadPatientAppointments(patientId) {
    try {
        const response = await fetch(`/api/patients/${patientId}/appointments/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        const appointments = await response.json();
        document.getElementById('appointments').innerHTML = generateAppointmentsTable(appointments);
    } catch (error) {
        console.error('Error loading appointments:', error);
    }
}

async function loadPatientMedicalRecords(patientId) {
    try {
        const response = await fetch(`/api/patients/${patientId}/medical-records/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        const records = await response.json();
        document.getElementById('medicalRecords').innerHTML = generateMedicalRecordsTable(records);
    } catch (error) {
        console.error('Error loading medical records:', error);
    }
}

async function loadPatientPrescriptions(patientId) {
    try {
        const response = await fetch(`/api/patients/${patientId}/prescriptions/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        const prescriptions = await response.json();
        document.getElementById('prescriptions').innerHTML = generatePrescriptionsTable(prescriptions);
    } catch (error) {
        console.error('Error loading prescriptions:', error);
    }
}

async function loadPatientLabResults(patientId) {
    try {
        const response = await fetch(`/api/patients/${patientId}/lab-results/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        const results = await response.json();
        document.getElementById('labResults').innerHTML = generateLabResultsTable(results);
    } catch (error) {
        console.error('Error loading lab results:', error);
    }
}

// Helper functions to generate tables for each tab
function generateAppointmentsTable(appointments) {
    return `
        <table class="table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Doctor</th>
                    <th>Purpose</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${appointments.map(apt => `
                    <tr>
                        <td>${formatDate(apt.date)}</td>
                        <td>Dr. ${apt.doctorName}</td>
                        <td>${apt.purpose}</td>
                        <td>${getStatusBadge(apt.status)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function generateMedicalRecordsTable(records) {
    return `
        <table class="table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Doctor</th>
                </tr>
            </thead>
            <tbody>
                ${records.map(record => `
                    <tr>
                        <td>${formatDate(record.date)}</td>
                        <td>${record.type}</td>
                        <td>${record.description}</td>
                        <td>Dr. ${record.doctorName}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function generatePrescriptionsTable(prescriptions) {
    return `
        <table class="table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Doctor</th>
                    <th>Medications</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${prescriptions.map(prescription => `
                    <tr>
                        <td>${formatDate(prescription.date)}</td>
                        <td>Dr. ${prescription.doctorName}</td>
                        <td>${prescription.medications.length} items</td>
                        <td>${getStatusBadge(prescription.status)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function generateLabResultsTable(results) {
    return `
        <table class="table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Test Type</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                ${results.map(result => `
                    <tr>
                        <td>${formatDate(result.date)}</td>
                        <td>${result.testType}</td>
                        <td>${getStatusBadge(result.status)}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="viewLabResult(${result.id})">
                                View Result
                            </button>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}
