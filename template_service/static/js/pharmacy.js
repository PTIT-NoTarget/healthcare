document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const stockFilter = document.getElementById('stockFilter');
    const medicineTable = document.getElementById('medicineTable').getElementsByTagName('tbody')[0];
    const medicineForm = document.getElementById('medicineForm');
    const saveMedicineBtn = document.getElementById('saveMedicine');
    const saveStockAdjustmentBtn = document.getElementById('saveStockAdjustment');

    // Load initial data
    loadMedicines();
    loadStatistics();

    // Event listeners
    searchInput.addEventListener('input', debounce(filterMedicines, 300));
    categoryFilter.addEventListener('change', filterMedicines);
    stockFilter.addEventListener('change', filterMedicines);
    saveMedicineBtn.addEventListener('click', saveMedicine);
    saveStockAdjustmentBtn.addEventListener('click', updateStock);

    // Function to load medicines
    async function loadMedicines() {
        try {
            const response = await fetch('/api/medicines/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const medicines = await response.json();
            displayMedicines(medicines);
        } catch (error) {
            console.error('Error loading medicines:', error);
            showAlert('Error loading medicines. Please try again.', 'danger');
        }
    }

    // Function to load statistics
    async function loadStatistics() {
        try {
            const response = await fetch('/api/pharmacy/statistics/', {
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

    // Function to display medicines
    function displayMedicines(medicines) {
        medicineTable.innerHTML = medicines.map(medicine => `
            <tr>
                <td>${medicine.name}</td>
                <td>${medicine.category}</td>
                <td>${medicine.stock}</td>
                <td>$${medicine.unitPrice.toFixed(2)}</td>
                <td>${formatDate(medicine.expiryDate)}</td>
                <td>${getStockStatusBadge(medicine.stock, medicine.minStockLevel)}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="editMedicine(${medicine.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-success" onclick="openStockModal(${medicine.id})">
                            <i class="fas fa-boxes"></i>
                        </button>
                        <button class="btn btn-outline-info" onclick="viewMedicineDetails(${medicine.id})">
                            <i class="fas fa-info-circle"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // Function to update statistics
    function updateStatistics(stats) {
        document.getElementById('totalMedicines').textContent = stats.totalMedicines;
        document.getElementById('lowStockItems').textContent = stats.lowStockItems;
        document.getElementById('outOfStockItems').textContent = stats.outOfStockItems;
        document.getElementById('totalValue').textContent = `$${stats.totalValue.toFixed(2)}`;
    }

    // Function to save new medicine
    async function saveMedicine() {
        const formData = {
            name: document.getElementById('medicineName').value,
            category: document.getElementById('medicineCategory').value,
            stock: parseInt(document.getElementById('stockQuantity').value),
            unitPrice: parseFloat(document.getElementById('unitPrice').value),
            manufacturer: document.getElementById('manufacturer').value,
            expiryDate: document.getElementById('expiryDate').value,
            description: document.getElementById('description').value,
            minStockLevel: parseInt(document.getElementById('minStockLevel').value),
            storageLocation: document.getElementById('storageLocation').value
        };

        try {
            const response = await fetch('/api/medicines/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('addMedicineModal'));
                modal.hide();
                medicineForm.reset();
                loadMedicines();
                loadStatistics();
                showAlert('Medicine added successfully!', 'success');
            } else {
                throw new Error('Failed to add medicine');
            }
        } catch (error) {
            console.error('Error saving medicine:', error);
            showAlert('Error saving medicine. Please try again.', 'danger');
        }
    }

    // Function to update stock
    async function updateStock() {
        const medicineId = document.getElementById('editMedicineId').value;
        const adjustmentType = document.getElementById('adjustmentType').value;
        const quantity = parseInt(document.getElementById('adjustmentQuantity').value);
        const reason = document.getElementById('adjustmentReason').value;

        const adjustmentData = {
            medicineId,
            adjustmentType,
            quantity,
            reason
        };

        try {
            const response = await fetch('/api/medicines/stock-adjustment/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(adjustmentData)
            });

            if (response.ok) {
                const modal = bootstrap.Modal.getInstance(document.getElementById('editStockModal'));
                modal.hide();
                loadMedicines();
                loadStatistics();
                showAlert('Stock updated successfully!', 'success');
            } else {
                throw new Error('Failed to update stock');
            }
        } catch (error) {
            console.error('Error updating stock:', error);
            showAlert('Error updating stock. Please try again.', 'danger');
        }
    }

    // Function to filter medicines
    function filterMedicines() {
        // Implementation will be added based on backend API
        loadMedicines();
    }

    // Helper function for stock status badge
    function getStockStatusBadge(currentStock, minStock) {
        if (currentStock <= 0) {
            return '<span class="badge bg-danger">Out of Stock</span>';
        } else if (currentStock <= minStock) {
            return '<span class="badge bg-warning">Low Stock</span>';
        } else {
            return '<span class="badge bg-success">In Stock</span>';
        }
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

// Global functions for medicine actions
window.editMedicine = function(medicineId) {
    // Implementation will be added
    console.log('Edit medicine:', medicineId);
};

window.openStockModal = function(medicineId) {
    document.getElementById('editMedicineId').value = medicineId;
    const modal = new bootstrap.Modal(document.getElementById('editStockModal'));
    modal.show();
};

window.viewMedicineDetails = function(medicineId) {
    // Implementation will be added
    console.log('View medicine details:', medicineId);
};
