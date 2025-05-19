document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const testTypeFilter = document.getElementById('testTypeFilter');
    const testTable = document.getElementById('testTable').getElementsByTagName('tbody')[0];
    const testForm = document.getElementById('testForm');
    const saveTestBtn = document.getElementById('saveTest');
    const saveResultsBtn = document.getElementById('saveResults');

    // Load initial data
    loadTests();
    loadStatistics();
    loadDoctors();
    loadPatients();

    // Event listeners
    searchInput.addEventListener('input', debounce(filterTests, 300));
    statusFilter.addEventListener('change', filterTests);
    testTypeFilter.addEventListener('change', filterTests);
    saveTestBtn.addEventListener('click', saveTest);
    saveResultsBtn.addEventListener('click', saveTestResults);

    // Function to load tests
    async function loadTests() {
        try {
            const response = await fetch('/api/laboratory/tests/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const tests = await response.json();
            displayTests(tests);
        } catch (error) {
            console.error('Error loading tests:', error);
            showAlert('Error loading tests. Please try again.', 'danger');
        }
    }

    // Function to load statistics
    async function loadStatistics() {
        try {
            const response = await fetch('/api/laboratory/statistics/', {
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
        }
    }

    // Function to display tests
    function displayTests(tests) {
        testTable.innerHTML = tests.map(test => `
            <tr>
                <td>${test.id}</td>
                <td>${test.patientName}</td>
                <td>${formatTestType(test.testType)}</td>
                <td>Dr. ${test.doctorName}</td>
                <td>${formatDate(test.dateRequested)}</td>
                <td>${getStatusBadge(test.status)}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="viewTestDetails(${test.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="updateTestResults(${test.id})">
                            <i class="fas fa-flask"></i>
                        </button>
                        <button class="btn btn-outline-info" onclick="printTestReport(${test.id})">
                            <i class="fas fa-print"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // Function to update statistics
    function updateStatistics(stats) {
        document.getElementById('totalTests').textContent = stats.totalTests;
        document.getElementById('pendingTests').textContent = stats.pendingTests;
        document.getElementById('inProgressTests').textContent = stats.inProgressTests;
        document.getElementById('completedToday').textContent = stats.completedToday;
    }

    // Function to save new test
    async function saveTest() {
        const formData = {
            patientId: document.getElementById('patientSelect').value,
            testType: document.getElementById('testType').value,
            doctorId: document.getElementById('doctorSelect').value,
            priority: document.getElementById('priority').value,
            notes: document.getElementById('testNotes').value
        };

        try {
            const response = await fetch('/api/laboratory/tests/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('newTestModal'));
                modal.hide();
                testForm.reset();
                loadTests();
                loadStatistics();
                showAlert('Test request created successfully!', 'success');
            } else {
                throw new Error('Failed to create test request');
            }
        } catch (error) {
            console.error('Error saving test:', error);
            showAlert('Error creating test request. Please try again.', 'danger');
        }
    }

    // Function to save test results
    async function saveTestResults() {
        const formData = {
            testId: document.getElementById('testId').value,
            status: document.getElementById('testStatus').value,
            results: document.getElementById('testResults').value,
            technicianNotes: document.getElementById('technicianNotes').value,
            completionDate: document.getElementById('completionDate').value
        };

        try {
            const response = await fetch(`/api/laboratory/tests/${formData.testId}/results/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('testResultsModal'));
                modal.hide();
                loadTests();
                loadStatistics();
                showAlert('Test results saved successfully!', 'success');
            } else {
                throw new Error('Failed to save test results');
            }
        } catch (error) {
            console.error('Error saving test results:', error);
            showAlert('Error saving test results. Please try again.', 'danger');
        }
    }

    // Function to filter tests
    function filterTests() {
        const searchTerm = searchInput.value.toLowerCase();
        const status = statusFilter.value;
        const testType = testTypeFilter.value;

        loadTests(); // In real implementation, these filters would be passed to the API
    }

    // Helper function for test type formatting
    function formatTestType(type) {
        return type.split('_').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    // Helper function for status badge
    function getStatusBadge(status) {
        const badges = {
            'pending': 'warning',
            'in_progress': 'info',
            'completed': 'success',
            'cancelled': 'danger'
        };
        const color = badges[status] || 'secondary';
        return `<span class="badge bg-${color}">${formatTestType(status)}</span>`;
    }

    // Helper function to format date
    function formatDate(dateString) {
        return new Date(dateString).toLocaleString();
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

// Global functions for test actions
window.viewTestDetails = async function(testId) {
    try {
        const response = await fetch(`/api/laboratory/tests/${testId}/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        const test = await response.json();
        // Implementation for viewing test details
        console.log('View test details:', test);
    } catch (error) {
        console.error('Error loading test details:', error);
        showAlert('Error loading test details. Please try again.', 'danger');
    }
};

window.updateTestResults = function(testId) {
    document.getElementById('testId').value = testId;
    const modal = new bootstrap.Modal(document.getElementById('testResultsModal'));
    modal.show();
};

window.printTestReport = function(testId) {
    window.open(`/api/laboratory/tests/${testId}/report/`, '_blank');
};
