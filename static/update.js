document.addEventListener('DOMContentLoaded', async () => {
    const roleDropdown = document.getElementById('roleDropdown');
    
    // Fetch roles and populate the dropdown
    async function fetchRoles() {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                alert('Please log in to fetch roles.');
                return;
            }
            const response = await fetch('/SuperAdmin_get_roles', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const roles = await response.json();
                roles.forEach(role => {
                    const option = document.createElement('option');
                    option.value = role.role_name;
                    option.textContent = role.role_name;
                    roleDropdown.appendChild(option);
                });
            } else {
                alert('Failed to fetch roles');
            }
        } catch (error) {
            console.error('Error fetching roles:', error);
        }
    }
    fetchRoles();
});





// _________________________________________________________________________________________
// Function to handle form submission
document.getElementById('updateForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const user_id = sessionStorage.getItem('user_id');

    console.log("user_id",user_id)  // Pass user_id from template context
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const role = document.getElementById('roleDropdown').value;  // Ensure the correct name attribute
    
    // Get the JWT token from localStorage
    const token = localStorage.getItem('access_token');  // Adjust as needed

    if (!token) {
        alert('No valid token found!');
        return;
    }

    try {
        // Sending the data to the FastAPI endpoint
        console.log("user Id",user_id)
        console.log("role",role)
        const response = await fetch(`/admin_update/${user_id}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            
            body: new URLSearchParams({
                username: username,
                email: email,
                role: role,
            }),
        });
        
        const data = await response.json();

        console.log('data',data)

        if (response.ok) {
            alert('User updated successfully');
            sessionStorage.removeItem('user_id');
            
        } else {
            alert(data.detail || 'Failed to update user');
        }
    } catch (error) {
        console.error('Error updating user:', error);
        alert('Failed to update user.');
    }
});