// Payment Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    loadPendingPayments();
    loadPaymentHistory();

    // Event listeners
    document.getElementById('paymentMethodForm')?.addEventListener('submit', handlePaymentMethodSubmission);
});

function loadPendingPayments() {
    fetch('/api/payments/pending/', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        const pendingContainer = document.getElementById('pendingPayments');
        if (!pendingContainer) return;

        data.forEach(payment => {
            const card = createPaymentCard(payment, true);
            pendingContainer.appendChild(card);
        });

        updatePaymentStats(data);
    })
    .catch(error => console.error('Error loading pending payments:', error));
}

function loadPaymentHistory() {
    fetch('/api/payments/history/', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        const historyContainer = document.getElementById('paymentHistory');
        if (!historyContainer) return;

        data.forEach(payment => {
            const card = createPaymentCard(payment, false);
            historyContainer.appendChild(card);
        });
    })
    .catch(error => console.error('Error loading payment history:', error));
}

function createPaymentCard(payment, isPending) {
    const card = document.createElement('div');
    card.className = 'payment-card mb-3';

    const statusClass = getStatusClass(payment.status);
    const payButton = isPending ? `
        <button class="btn btn-primary" onclick="processPayment('${payment.id}')">
            Pay Now
        </button>
    ` : '';

    card.innerHTML = `
        <div class="payment-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">${payment.service_type} - #${payment.reference_number}</h6>
            <span class="badge ${statusClass}">${payment.status}</span>
        </div>
        <div class="payment-body">
            <div class="payment-item">
                <div class="row">
                    <div class="col-md-8">
                        <p class="mb-1"><strong>Description:</strong> ${payment.description}</p>
                        <p class="mb-1"><strong>Date:</strong> ${new Date(payment.created_at).toLocaleDateString()}</p>
                    </div>
                    <div class="col-md-4 text-md-end">
                        <h5 class="mb-3">$${payment.amount.toFixed(2)}</h5>
                        ${payButton}
                    </div>
                </div>
            </div>
        </div>
    `;

    return card;
}

function processPayment(paymentId) {
    // Show payment modal
    const modal = new bootstrap.Modal(document.getElementById('paymentModal'));
    modal.show();

    // Store payment ID for processing
    document.getElementById('currentPaymentId').value = paymentId;

    // Load payment details
    fetch(`/api/payments/${paymentId}/`, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
    })
    .then(response => response.json())
    .then(payment => {
        document.getElementById('paymentAmount').textContent = `$${payment.amount.toFixed(2)}`;
        document.getElementById('paymentDescription').textContent = payment.description;
    })
    .catch(error => console.error('Error loading payment details:', error));
}

function handlePaymentMethodSubmission(event) {
    event.preventDefault();

    const paymentId = document.getElementById('currentPaymentId').value;
    const formData = new FormData(event.target);
    const paymentMethod = formData.get('paymentMethod');

    fetch(`/api/payments/${paymentId}/process/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({
            payment_method: paymentMethod
        })
    })
    .then(response => response.json())
    .then(data => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
        modal.hide();

        showAlert('Payment processed successfully!', 'success');
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    })
    .catch(error => {
        console.error('Error processing payment:', error);
        showAlert('Error processing payment. Please try again.', 'danger');
    });
}

function getStatusClass(status) {
    switch (status.toLowerCase()) {
        case 'pending':
            return 'bg-warning';
        case 'completed':
            return 'bg-success';
        case 'failed':
            return 'bg-danger';
        default:
            return 'bg-secondary';
    }
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.row'));
    setTimeout(() => alertDiv.remove(), 3000);
}

function updatePaymentStats(payments) {
    const totalAmount = payments.reduce((sum, payment) => sum + payment.amount, 0);
    document.getElementById('pendingCount').textContent = payments.length;
    document.getElementById('totalAmount').textContent = `$${totalAmount.toFixed(2)}`;
}
