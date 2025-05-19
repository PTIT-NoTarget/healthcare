document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = '';
            messageDiv.className = 'mt-3 text-center';

            if (!username || !password) {
                messageDiv.textContent = 'Please enter both username and password.';
                messageDiv.classList.add('text-danger');
                return;
            }

            try {
                const response = await fetch('/api/auth/token/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    messageDiv.textContent = 'Login successful! Redirecting...';
                    messageDiv.classList.add('text-success');
                    localStorage.setItem('authToken', data.access);
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1000);
                } else {
                    let errorMessage = 'Login failed. ';
                    if (data.detail) {
                        errorMessage += data.detail;
                    } else if (data.error) {
                        errorMessage += data.error;
                    } else if (typeof data === 'object') {
                        errorMessage += Object.values(data).flat().join(' ');
                    }
                    console.error('Login error response:', data);
                    messageDiv.textContent = errorMessage;
                    messageDiv.classList.add('text-danger');
                }
            } catch (error) {
                console.error('Login error:', error);
                messageDiv.textContent = 'Network error or server not responding. Please try again later.';
                messageDiv.classList.add('text-danger');
            }
        });
    }
});

