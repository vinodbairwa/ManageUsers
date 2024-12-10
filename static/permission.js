const token = localStorage.getItem('access_token'); // Retrieve the JWT token
// Function to fetch permissions and populate the dropdown
async function fetchPermissions() {
    try {
        const response = await fetch('/get_permissions', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const permissions = await response.json();
            const dropdown = document.getElementById('permissions');
            dropdown.innerHTML = ''; // Clear existing options

            permissions.forEach(permission => {
                const option = document.createElement('option');
                option.value = permission.id;
                option.textContent = permission.permission_name;
                dropdown.appendChild(option);
            });
        } else {
            alert('Failed to fetch permissions');
        }
    } catch (error) {
        console.error('Error fetching permissions:', error);
    }
}

// Function to delete the selected permission
async function deletePermission() {
    const dropdown = document.getElementById('permissions');
    const selectedPermissionId = dropdown.value;

    if (!selectedPermissionId) {
        alert('Please select a permission to delete.');
        return;
    }

    if (!confirm('Are you sure you want to delete this permission?')) {
        return; // Cancel deletion
    }

    try {
        const response = await fetch(`/permission_delete/${selectedPermissionId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            alert('Permission deleted successfully');
            fetchPermissions(); // Refresh the dropdown
        } else {
            const error = await response.json();
            alert('Error deleting permission: ' + error.detail);
        }
    } catch (error) {
        console.error('Error deleting permission:', error);
    }
}

// Attach event listener to the delete button
document.getElementById('deletePermissionButton').addEventListener('click', deletePermission);

// Fetch permissions on page load
window.onload = fetchPermissions;


//___________________________

// Add event listener to the form submit
document.getElementById('permissionForm').addEventListener('submit', async function (event) {
event.preventDefault(); // Prevent the default form submit behavior

// Retrieve the token (e.g., from localStorage or wherever you have it)
const token = localStorage.getItem('access_token'); // Assuming token is saved in localStorage
console.log(token)
// Get the permission name from the input field
const permissionName = document.getElementById('permission_name').value;

// Prepare the form data
const formData = new FormData();
formData.append('permission_name', permissionName);

try {
    // Send the request to create the permission
    const response = await fetch('http://127.0.0.1:8000/permission_create/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}` // Send the token in the Authorization header
        },
        body: formData
    });

    if (response.ok) {
        alert('Permission created successfully');
        const data = await response.text(); // Get the response as text (since it's HTML)
     
    } else {
        const errorData = await response.json();
        document.getElementById('message').innerHTML = "Error: " + errorData.detail;
    }
} catch (error) {
    console.error('Request failed', error);
    document.getElementById('message').innerHTML = "Request failed.";
}
}); 



