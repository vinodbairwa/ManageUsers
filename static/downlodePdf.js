// document.getElementById('downloadCsvBtn').addEventListener('click', async function() {
//     try {
//         // Get the JWT token from localStorage (assuming it's stored there after login)
//         const token = localStorage.getItem('access_token');
        
//         if (!token) {
//             alert('You need to log in first.');
//             return;
//         }

//         // Send a GET request to the /download_permission_csv endpoint with the token in the headers
//         const response = await fetch('/download_permission_csv', {
//             method: 'GET',
//             headers: {
//                 'Authorization': `Bearer ${token}`,  // Include the token in the Authorization header
//             },
//         });

//         // Check if the response is OK (status 200)
//         if (response.ok) {
//             // Create a link element to trigger the file download
//             const link = document.createElement('a');
//             link.href = URL.createObjectURL(await response.blob());  // Get the CSV file as a Blob
//             link.download = 'permissions.csv';  // Set the default filename
//             link.click();  // Programmatically click the link to trigger the download
//         } else {
//             const errorData = await response.json();
//             alert('Error downloading CSV: ' + errorData.detail || 'Unknown error');
//         }
//     } catch (error) {
//         console.error('Error:', error);
//         alert('An error occurred while downloading the file.');
//     }
// });

























  // General function to handle download logic
  const downloadCsv = async (apiUrl, filename) => {
    try {
        // Get the JWT token from localStorage (assuming it's stored there after login)
        const token = localStorage.getItem('access_token');
        
        if (!token) {
            alert('You need to log in first.');
            return;
        }

        // Send a GET request to the provided API URL with the token in the headers
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,  // Include the token in the Authorization header
            },
        });

        // Check if the response is OK (status 200)
        if (response.ok) {
            // Create a link element to trigger the file download
            const link = document.createElement('a');
            link.href = URL.createObjectURL(await response.blob());  // Get the file as a Blob
            link.download = filename;  // Set the filename dynamically
            link.click();  // Programmatically click the link to trigger the download
        } else {
            const errorData = await response.json();
            alert('Error downloading CSV: ' + (errorData.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while downloading the file.');
    }
};

// Event listener for downloading Roles CSV
document.getElementById('downloadRoleCsvBtn').addEventListener('click', () => {
    downloadCsv('/download_roles_csv', 'roles.csv');  // Call function with appropriate API endpoint and filename
});

// Event listener for downloading User Data CSV
document.getElementById('downloadUserDataCsvBtn').addEventListener('click', () => {
    downloadCsv('/download_users_csv', 'user_data.csv');  // Call function with appropriate API endpoint and filename
});

// Event listener for downloading Permissions CSV
document.getElementById('downloadPermissionCsvBtn').addEventListener('click', () => {
    downloadCsv('/download_permission_csv', 'permissions.csv');  // Call function with appropriate API endpoint and filename
});