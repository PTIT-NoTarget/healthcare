// Inventory Management JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initial load of inventory data
    loadInventoryData();

    // Filter event listeners
    document.getElementById('itemTypeFilter').addEventListener('change', filterInventory);
    document.getElementById('locationFilter').addEventListener('change', filterInventory);
    document.getElementById('statusFilter').addEventListener('change', filterInventory);
    document.getElementById('searchInput').addEventListener('input', filterInventory);

    // Form submission handlers
    document.getElementById('saveItemBtn').addEventListener('click', saveNewItem);
    document.getElementById('confirmTransferBtn').addEventListener('click', transferItem);
});

function loadInventoryData() {
    fetch('/api/inventory/items/', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        updateInventoryTable(data);
        updateInventoryStats(data);
    })
    .catch(error => console.error('Error loading inventory:', error));
}

function updateInventoryTable(data) {
    const tbody = document.getElementById('inventoryTableBody');
    tbody.innerHTML = '';

    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.item_name}</td>
            <td>${item.item_type}</td>
            <td>${item.location_type}</td>
            <td>${item.quantity}</td>
            <td>${item.unit_of_measure}</td>
            <td><span class="badge ${getStatusBadgeClass(item.status)}">${item.status}</span></td>
            <td>${item.expiration_date || 'N/A'}</td>
            <td>
                <button class="btn btn-sm btn-info me-1" onclick="viewItem(${item.id})">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-primary me-1" onclick="editItem(${item.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-success me-1" onclick="openTransferModal(${item.id})">
                    <i class="fas fa-exchange-alt"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function updateInventoryStats(data) {
    document.getElementById('totalItems').textContent = data.length;
    document.getElementById('lowStockItems').textContent = data.filter(item => item.status === 'Low Stock').length;
    document.getElementById('outOfStockItems').textContent = data.filter(item => item.status === 'Out of Stock').length;
    document.getElementById('expiringSoonItems').textContent = data.filter(item => {
        if (!item.expiration_date) return false;
        const expiryDate = new Date(item.expiration_date);
        const thirtyDaysFromNow = new Date();
        thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);
        return expiryDate <= thirtyDaysFromNow && expiryDate > new Date();
    }).length;
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'Available': return 'bg-success';
        case 'Low Stock': return 'bg-warning';
        case 'Out of Stock': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

function filterInventory() {
    const itemType = document.getElementById('itemTypeFilter').value;
    const location = document.getElementById('locationFilter').value;
    const status = document.getElementById('statusFilter').value;
    const search = document.getElementById('searchInput').value.toLowerCase();

    let url = '/api/inventory/items/?';
    if (itemType) url += `item_type=${itemType}&`;
    if (location) url += `location_type=${location}&`;
    if (status) url += `status=${status}&`;
    if (search) url += `search=${search}`;

    fetch(url, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        updateInventoryTable(data);
        updateInventoryStats(data);
    })
    .catch(error => console.error('Error filtering inventory:', error));
}

function saveNewItem() {
    const form = document.getElementById('addItemForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    fetch('/api/inventory/items/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('addItemModal'));
        modal.hide();
        loadInventoryData();
        form.reset();
        showAlert('Item added successfully', 'success');
    })
    .catch(error => {
        console.error('Error saving item:', error);
        showAlert('Error adding item', 'danger');
    });
}

function transferItem() {
    const form = document.getElementById('transferForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    fetch(`/api/inventory/items/${data.item_id}/transfer/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
            location_type: data.new_location,
            quantity: parseInt(data.transfer_quantity)
        })
    })
    .then(response => response.json())
    .then(data => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('transferItemModal'));
        modal.hide();
        loadInventoryData();
        form.reset();
        showAlert('Item transferred successfully', 'success');
    })
    .catch(error => {
        console.error('Error transferring item:', error);
        showAlert('Error transferring item', 'danger');
    });
}

function viewItem(id) {
    fetch(`/api/inventory/items/${id}/`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
    })
    .then(response => response.json())
    .then(item => {
        // Populate view modal with item details
        document.getElementById('viewItemDetails').innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Item Name:</strong> ${item.item_name}</p>
                    <p><strong>Type:</strong> ${item.item_type}</p>
                    <p><strong>Location:</strong> ${item.location_type}</p>
                    <p><strong>Quantity:</strong> ${item.quantity} ${item.unit_of_measure}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Status:</strong> ${item.status}</p>
                    <p><strong>Expiration Date:</strong> ${item.expiration_date || 'N/A'}</p>
                    <p><strong>Last Restocked:</strong> ${item.last_restock_date || 'N/A'}</p>
                    <p><strong>Reorder Level:</strong> ${item.reorder_level}</p>
                </div>
            </div>
        `;
        const modal = new bootstrap.Modal(document.getElementById('viewItemModal'));
        modal.show();
    })
    .catch(error => console.error('Error viewing item:', error));
}

function editItem(id) {
    fetch(`/api/inventory/items/${id}/`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
    })
    .then(response => response.json())
    .then(item => {
        // Populate edit form with item details
        const form = document.getElementById('editItemForm');
        Object.keys(item).forEach(key => {
            const input = form.elements[key];
            if (input) input.value = item[key];
        });
        document.getElementById('editItemId').value = id;
        const modal = new bootstrap.Modal(document.getElementById('editItemModal'));
        modal.show();
    })
    .catch(error => console.error('Error editing item:', error));
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.card'));
    setTimeout(() => alertDiv.remove(), 3000);
}
