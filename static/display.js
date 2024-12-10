// // Assuming `token` is stored in localStorage
// let token;

// // Function to create permission
// async function createPermission(permissionName) {
//     token = localStorage.getItem('access_token'); 
    
//     // Check if token exists
//     if (!token) {
//         console.error('No token found. Please log in.');
//         document.getElementById('message').innerText = "No token found. Please log in.";
//         return;
//     }

//     try {
//         const response = await fetch('http://127.0.0.1:8000/permission_create/', {
//             method: 'POST',
//             headers: {
//                 'Authorization': `Bearer ${token}`,  // Include the token in the Authorization header
//                 'Content-Type': 'application/x-www-form-urlencoded', // For FormData
//             },
//             body: new URLSearchParams({
//                 permission_name: permissionName,  // Send the permission name in the body
//             })
//         });
        
//         if (response.ok) {
//             const data = await response.text();  // Get response as text
//             console.log('Permission created successfully:', data);  // Log success
//             document.getElementById('message').innerText = "Permission created successfully!";
            
//             // Update the URL with the new permission name
//             window.history.pushState({}, '', `/SuperAdminDeshbord?permission_name=${permissionName}`);
//         } else {
//             // If response is not OK, log the error and display the error message
//             const errorData = await response.json();
//             console.error('Error response from server:', errorData);  // Log the error
//             document.getElementById('message').innerText = `Error: ${errorData.detail}`;
//         }
//     } catch (error) {
//         console.error('Error creating permission:', error);
//         document.getElementById('message').innerText = "Error creating permission.";
//     }
// }

// // Example usage:
// // This will be triggered when the "Create Permission" button is clicked.
// document.getElementById('createPermissionButton')?.addEventListener('click', () => {
//     const permissionName = 'hgfb';  // This can be dynamically fetched from user input
//     createPermission(permissionName);  // Call this function with the desired permission name
// });
