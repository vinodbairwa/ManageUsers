const token = localStorage.getItem('access_token');
console.log("Token from localStorage: ", token);

document.getElementById('logoutButton').addEventListener('click', async function() {
    try {
        console.log("Start logout request");

        // Check if token exists
        if (!token) {
            alert('No token found in localStorage!');
            return;
        }

        // Send a POST request to the logout endpoint
        const response = await fetch('http://127.0.0.1:8000/logout/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            }
        });

        console.log("Logout request sent");

        if (response.ok) {
            // Remove the JWT token from localStorage
            localStorage.removeItem('access_token');

            alert('You have been logged out.');
            window.location.href = '/';  // Redirect to the home page or login page
        } else {
            const error = await response.text(); // Get error text
            console.error('Logout failed:', error);
            alert('Logout failed. Please try again.');
        }
    } catch (error) {
        console.error('Error during logout:', error);
        alert('An error occurred while logging out.');
    }
});





