document.addEventListener('DOMContentLoaded', function() {
    const authToken = localStorage.getItem('authToken');
    const authButtons = document.querySelectorAll('.auth-buttons');
    const userProfileMenu = document.getElementById('userProfileMenu');
    const usernameSpan = document.getElementById('username');
    const logoutButton = document.getElementById('logoutButton');

    async function fetchUserProfile() {
        try {
            const response = await fetch('/api/auth/profile/', {
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });

            if (response.ok) {
                const userData = await response.json();
                usernameSpan.textContent = userData.username;

                // Show profile menu and hide auth buttons
                userProfileMenu.classList.remove('d-none');
                authButtons.forEach(button => button.classList.add('d-none'));
            } else {
                // If profile fetch fails, treat as logged out
                handleLogout();
            }
        } catch (error) {
            console.error('Error fetching user profile:', error);
            handleLogout();
        }
    }

    function handleLogout() {
        localStorage.removeItem('authToken');
        userProfileMenu.classList.add('d-none');
        authButtons.forEach(button => button.classList.remove('d-none'));

        // Redirect to login if not already there
        if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login/';
        }
    }

    // Add logout handler
    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    }

    // Check auth status and fetch profile if logged in
    if (authToken) {
        fetchUserProfile();
    } else {
        // Show auth buttons if not logged in
        authButtons.forEach(button => button.classList.remove('d-none'));
        userProfileMenu.classList.add('d-none');
    }
});
