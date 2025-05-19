document.addEventListener('DOMContentLoaded', function () {
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const username = document.getElementById('regUsername').value;
            const email = document.getElementById('regEmail').value;
            const password = document.getElementById('regPassword').value;
            const confirmPassword = document.getElementById('regConfirmPassword').value;
            const messageDiv = document.getElementById('registerMessage');
            messageDiv.textContent = '';
            messageDiv.className = 'mt-3 text-center';

            if (!username || !email || !password || !confirmPassword) {
                messageDiv.textContent = 'Please fill in all fields.';
                messageDiv.classList.add('text-danger');
                return;
            }

            if (password !== confirmPassword) {
                messageDiv.textContent = 'Passwords do not match.';
                messageDiv.classList.add('text-danger');
                return;
            }

            try {
                // Replace with your actual API endpoint for registration
                const response = await fetch('/api/auth/register/', { // Example API endpoint
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    messageDiv.textContent = 'Registration successful! Please login.';
                    messageDiv.classList.add('text-success');
                    // Optionally redirect to login page or auto-login
                    setTimeout(() => { window.location.href = '/login/'; }, 2000);
                } else {
                    let errorMessage = 'Registration failed.';
                    if (data) {
                        errorMessage = Object.values(data).flat().join(' ');
                    }
                    messageDiv.textContent = errorMessage;
                    messageDiv.classList.add('text-danger');
                }
            } catch (error) {
                console.error('Registration error:', error);
                messageDiv.textContent = 'An error occurred during registration. Please try again.';
                messageDiv.classList.add('text-danger');
            }
        });
    }
});
