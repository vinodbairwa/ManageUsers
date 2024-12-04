
function goToPermissionPage(pageName) {
    // Retrieve the JWT token from storage (localStorage/sessionStorage)
    const token = localStorage.getItem("access_token"); // or sessionStorage
    
    console.log(pageName)
    const url = pageName
    // Check if the token exists
    if (!token) {
        alert("Unauthorized access: JWT token is missing.");
        return;
    }

    // Create a new request to the /permission endpoint with the pageName
    fetch(`/Render/${url}`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            // If the token is valid and the page is accessible, navigate to the dynamic page
            window.location.href = `/static/${url}.html`;  // Dynamically navigate
        } else {
            throw new Error('Unauthorized access');
        }
    })
    .catch(error => {
        alert("Error: " + error.message);  // Handle error (invalid token or other issues)
    });
}







// function goToUpdatePage(user_id) {
//     // Retrieve the JWT token from storage (localStorage/sessionStorage)
//     const token = localStorage.getItem("access_token"); // or sessionStorage
 
    
//     console.log("User ID:", user_id);

//     // Check if the token exists
//     if (!token) {
//         alert("Unauthorized access: JWT token is missing.");
//         return;
//     }


//     // Create a new request to the /permission endpoint with the pageName
//     fetch(`/SuperAdmin/update/${user_id}`, {
//         method: 'GET',
//         headers: {
//             'Authorization': `Bearer ${token}`
//         }
//     })
//     .then(response => {
//         if (response.ok) {
//             // If the token is valid and the page is accessible, navigate to the dynamic page
//             window.location.href = '/static/update.html';  // Dynamically navigate
//         } else {
//             throw new Error('Unauthorized access');
//         }
//     })
//     .catch(error => {
//         alert("Error: " + error.message);  // Handle error (invalid token or other issues)
//     });
// }












// function goToPermissionPage(pageName) {
    
//     // Retrieve the JWT token from storage (localStorage/sessionStorage)
//     const token = localStorage.getItem("access_token"); // or sessionStorage

//     // Check if the token exists
//     if (!token) {
//         alert("Unauthorized access: JWT token is missing.");
//         return;
//     }

//     // Create a new request to the /permission page with the token in the headers
//     fetch(`/api/${pageName}`, {
//         method: 'GET',
//         headers: {
//             'Authorization': `Bearer ${token}`
//         }
//     })
//     .then(response => {
//         if (response.ok) {
//             // If the token is valid and the page is accessible, navigate to /add_permission.html
//             window.location.href = `/static/${pageName}.html`;  // Navigate to the static file location
          
//         } else {
//             throw new Error('Unauthorized access');
//         }
//     })
//     .catch(error => {
//         alert("Error: " + error.message);  // Handle error (invalid token or other issues)
//     });
// }


// =____________________________



// function goToRolePage() {
//     // Retrieve the JWT token from storage (localStorage/sessionStorage)
//     const token = localStorage.getItem("access_token"); // or sessionStorage

//     // Check if the token exists
//     if (!token) {
//         alert("Unauthorized access: JWT token is missing.");
//         return;
//     }

//     // Create a new request to the /permission page with the token in the headers
//     fetch('/role_create_render/', {
//         method: 'GET',
//         headers: {
//             'Authorization': `Bearer ${token}`
//         }
//     })
//     .then(response => {
//         if (response.ok) {
//             // If the token is valid and the page is accessible, navigate to /add_permission.html
//             window.location.href ='/static/AddRole.html';  // Navigate to the static file location
          
//         } else {
//             throw new Error('Unauthorized access');
//         }
//     })
//     .catch(error => {
//         alert("Error: " + error.message);  // Handle error (invalid token or other issues)
//     });
// }



// // ________________UserRole page

// function goToUserRolePage() {
//     // Retrieve the JWT token from storage (localStorage/sessionStorage)
//     const token = localStorage.getItem("access_token"); // or sessionStorage

//     // Check if the token exists
//     if (!token) {
//         alert("Unauthorized access: JWT token is missing.");
//         return;
//     }

//     // Create a new request to the /permission page with the token in the headers
//     fetch('/user_role_render_page/', {
//         method: 'GET',
//         headers: {
//             'Authorization': `Bearer ${token}`
//         }
//     })
//     .then(response => {
        
//         if (response.ok) {
//             // If the token is valid and the page is accessible, navigate to /useroleDrop.htm
//             console.log("sucesssssss")
//             window.location.href ='/static/useroleDrop.html';  // Navigate to the static file location
          
//         } else {
//             throw new Error('Unauthorized access');
//         }
//     })
//     .catch(error => {
//         alert("Error: " + error.message);  // Handle error (invalid token or other issues)
//     });
// }




// // permission role
// function goToPermissionRolePage() {
//     // Retrieve the JWT token from storage (localStorage/sessionStorage)
//     const token = localStorage.getItem("access_token"); // or sessionStorage

//     // Check if the token exists
//     if (!token) {
//         alert("Unauthorized access: JWT token is missing.");
//         return;
//     }

//     fetch('/Allpermission/', {
//         method: 'GET',
//         headers: {
//             'Authorization': `Bearer ${token}`
//         }
//     })
//     .then(response => {
        
//         if (response.ok) {
//             // If the token is valid and the page is accessible, navigate to /useroleDrop.htm
//             console.log("sucesssssss")
//             window.location.href ='/static/per_role.html';  // Navigate to the static file location
          
//         } else {
//             throw new Error('Unauthorized access');
//         }
//     })
//     .catch(error => {
//         alert("Error: " + error.message);  // Handle error (invalid token or other issues)
//     });
// }



// // __________________Current User Update___

// function goToCurrent_User_UpdatePage() {
//     // Retrieve the JWT token from storage (localStorage/sessionStorage)
//     const token = localStorage.getItem("access_token"); // or sessionStorage

//     // Check if the token exists
//     if (!token) {
//         alert("Unauthorized access: JWT token is missing.");
//         return;
//     }

//     fetch('/Allpermission/', {
//         method: 'GET',
//         headers: {
//             'Authorization': `Bearer ${token}`
//         }
//     })
//     .then(response => {
        
//         if (response.ok) {
//             // If the token is valid and the page is accessible, navigate to /useroleDrop.htm
//             console.log("sucesssssss")
//             window.location.href ='/static/per_role.html';  // Navigate to the static file location
          
//         } else {
//             throw new Error('Unauthorized access');
//         }
//     })
//     .catch(error => {
//         alert("Error: " + error.message);  // Handle error (invalid token or other issues)
//     });
// }

