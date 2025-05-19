document.addEventListener('DOMContentLoaded', function() {
    loadUserProfile();
    initializeFormHandlers();

    async function loadUserProfile() {
        try {
            const response = await fetch('/api/auth/profile/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const userData = await response.json();

            // Update profile information
            updateProfileDisplay(userData);

            // If user is a doctor, load additional doctor information
            if (userData.role === 'doctor') {
                loadDoctorInfo(userData.id);
            }

            // Load recent activity and statistics
            loadRecentActivity();
            loadUserStats();
        } catch (error) {
            console.error('Error loading profile:', error);
            showAlert('Error loading profile information', 'danger');
        }
    }

    async function loadDoctorInfo(userId) {
        try {
            const response = await fetch(`/api/doctors/${userId}/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const doctorData = await response.json();

            // Show doctor-specific fields
            document.querySelectorAll('.doctor-specific').forEach(el => el.style.display = 'flex');

            // Update doctor-specific information
            document.getElementById('profileSpecialization').textContent = doctorData.specialization;
            document.getElementById('detailLicense').textContent = doctorData.license_number;
        } catch (error) {
            console.error('Error loading doctor info:', error);
        }
    }

    function updateProfileDisplay(userData) {
        // Update profile section
        document.getElementById('profileName').textContent = userData.name || userData.username;
        document.getElementById('profileRole').textContent = capitalizeFirstLetter(userData.role || 'User');

        // Update details section
        document.getElementById('detailName
        document.getElementById('detailName').textContent = userData.name || userData.username;
        document.getElementById('detailEmail').textContent = userData.email || 'Not provided';
        document.getElementById('detailPhone').textContent = userData.phone || 'Not provided';

        // Update edit form
        document.getElementById('editName').value = userData.name || '';
        document.getElementById('editEmail').value = userData.email || '';
        document.getElementById('editPhone').value = userData.phone || '';
    }

    async function loadRecentActivity() {
        try {
            const response = await fetch('/api/activity/recent/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const activities = await response.json();

            const activityContainer = document.getElementById('recentActivity');
            activityContainer.innerHTML = activities.length ? '' : '<p class="text-muted">No recent activity</p>';

            activities.forEach(activity => {
                const activityElement = document.createElement('div');
                activityElement.className = 'mb-2';
                activityElement.innerHTML = `
                    <small class="text-muted">${formatDate(activity.timestamp)}</small>
                    <p class="mb-1">${activity.description}</p>
                `;
                activityContainer.appendChild(activityElement);
            });
        } catch (error) {
            console.error('Error loading recent activity:', error);
        }
    }

    async function loadUserStats() {
        try {
            const response = await fetch('/api/user/stats/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            const stats = await response.json();

            const statsContainer = document.getElementById('userStats');
            statsContainer.innerHTML = `
                <div class="d-flex justify-content-between mb-2">
                    <span>Total Appointments</span>
                    <span class="text-primary">${stats.total_appointments || 0}</span>
                </div>
                <div class="d-flex justify-content-between mb-2">
                    <span>Completed</span>
                    <span class="text-success">${stats.completed_appointments || 0}</span>
                </div>
                <div class="d-flex justify-content-between">
                    <span>Pending</span>
                    <span class="text-warning">${stats.pending_appointments || 0}</span>
                </div>
            `;
        } catch (error) {
            console.error('Error loading user stats:', error);
        }
    }

    function initializeFormHandlers() {
        // Edit Profile Form Handler
        const saveProfileBtn = document.getElementById('saveProfile');
        if (saveProfileBtn) {
            saveProfileBtn.addEventListener('click', async () => {
                const formData = {
                    name: document.getElementById('editName').value,
                    email: document.getElementById('editEmail').value,
                    phone: document.getElementById('editPhone').value
                };

                try {
                    const response = await fetch('/api/auth/profile/update/', {
                        method: 'PUT',
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });

                    if (response.ok) {
                        showAlert('Profile updated successfully!', 'success');
                        bootstrap.Modal.getInstance(document.getElementById('editProfileModal')).hide();
                        loadUserProfile();
                    } else {
                        const data = await response.json();
                        showAlert(data.message || 'Error updating profile', 'danger');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    showAlert('Error updating profile', 'danger');
                }
            });
        }

        // Change Password Form Handler
        const changePasswordBtn = document.getElementById('changePassword');
        if (changePasswordBtn) {
            changePasswordBtn.addEventListener('click', async () => {
                const currentPassword = document.getElementById('currentPassword').value;
                const newPassword = document.getElementById('newPassword').value;
                const confirmPassword = document.getElementById('confirmPassword').value;

                if (newPassword !== confirmPassword) {
                    showAlert('New passwords do not match', 'danger');
                    return;
                }

                try {
                    const response = await fetch('/api/auth/change-password/', {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            current_password: currentPassword,
                            new_password: newPassword
                        })
                    });

                    if (response.ok) {
                        showAlert('Password changed successfully!', 'success');
                        bootstrap.Modal.getInstance(document.getElementById('changePasswordModal')).hide();
                        document.getElementById('changePasswordForm').reset();
                    } else {
                        const data = await response.json();
                        showAlert(data.message || 'Error changing password', 'danger');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    showAlert('Error changing password', 'danger');
                }
            });
        }
    }

    // Utility Functions
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.container').insertAdjacentElement('afterbegin', alertDiv);
        setTimeout(() => alertDiv.remove(), 5000);
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
    }
});

