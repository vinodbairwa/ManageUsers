
let userData = []
document.addEventListener("DOMContentLoaded", function() {
    // Function to fetch user data and populate table
    function fetchUserData() {
        const token = localStorage.getItem("access_token");

        if (!token) {
            alert("Authorization token not found!");
            return;
        }

        fetch("/SuperAdminDeshbord_change", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
            },
        })
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector("#users-table tbody");
            tableBody.innerHTML = ""; // Clear existing rows

            userData = data.users_data
            data.users_data.forEach(user => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${user.user_id}</td>
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td>${user.roles.join(", ")}</td>
                    <td>${user.permissions.join(", ")}</td>

                  <td><a href="#"" class="btn-edit" data-userid="${user.user_id}" >Edit</a></td>
                   
                    <td><a href="#" class="btn-delete" data-username="${user.username}">Delete</a></td>
                `;
                tableBody.appendChild(row);
            });

            // Attach event listeners after populating rows
            attachEditButtonListeners();
            attachDeleteButtonListeners();
        })
        .catch(error => {
            console.error("Error fetching user data:", error);
        });
    }
     


//________________________  DELETE_______________________________________________________________________________ 
    // Function to handle delete button clicks
    function attachDeleteButtonListeners() {
        const deleteButtons = document.querySelectorAll(".btn-delete");

        deleteButtons.forEach(button => {
            button.addEventListener("click", function(event) {
                event.preventDefault(); // Prevent default anchor behavior
                const username = this.dataset.username;
                const token = localStorage.getItem("access_token");

                if (!token) {
                    alert("Authorization token not found!");
                    return;
                }

                if (confirm(`Are you sure you want to delete the user "${username}"?`)) {
                    fetch(`/users_delete/${username}`, {
                        method: "GET", // Adjust to DELETE if supported
                        headers: {
                            "Authorization": `Bearer ${token}`,
                            "Content-Type": "application/json",
                        },
                    })
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(error => {
                                throw new Error(error.detail || "Error deleting user");
                            });
                        }
                        return response.json();
                    })
                    .then(data => {
                        alert(`${username} deleted successfully!`);
                        fetchUserData(); // Refresh table after deletion
                    })
                    .catch(error => {
                        console.error("Error deleting user:", error);
                        alert(`Failed to delete user: ${error.message}`);
                    });
                }
            });
        });
    }


// ______________________ click Edit button___________________
let currentUser = {}

function attachEditButtonListeners() {
const editButtons = document.querySelectorAll(".btn-edit");

editButtons.forEach(button => {
    button.addEventListener("click", function(event) {
        event.preventDefault();  // Prevent default anchor behavior

        // Store the user_id in a variable and redirect
        const userId = this.dataset.userid;  // Get user ID from data attribute

        currentUser = userData.find((item) => {
            return  item.user_id === userId ? item : {}
        }
            
        ) || {}

        console.log("print current ",currentUser)

        console.log("current user", currentUser.username)

        if (!userId) {
            alert("User ID not found!");
            return;
        }

        // Store userId in session storage (or local storage)
        sessionStorage.setItem("user_id", userId);
        

        // Redirect to the update page
        window.location.href = "/static/update.html";
    });
});    
}

    fetchUserData();
});










// _____________________
// Function to handle loading and displaying the page content using XMLHttpRequest
// Function to show an error message inside the content container
// function showError(message) {
//     const contentContainer = document.getElementById('content-container');
//     contentContainer.innerHTML = `<p>Error: ${message}</p>`;
// }

// // Function to close the modal
// function closeModal() {
//     const contentContainer = document.getElementById('content-container');
//     const modalOverlay = document.getElementById('modalOverlay');
//     contentContainer.style.display = 'none';
//     modalOverlay.style.display = 'none';
// }

// // Function to load and execute a JS script
// function loadScript(src) {
//     const script = document.createElement('script');
//     script.src = src;
//     script.type = 'text/javascript';
//     script.async = true; // Load script asynchronously
//     document.body.appendChild(script);
// }

// // Function to handle loading and displaying page content
// async function loadPage(pageUrl) {
//     try {
//         const response = await fetch(pageUrl);  // Fetch page content

//         if (response.ok) {
//             const htmlContent = await response.text();  // Get HTML content
//             const contentContainer = document.getElementById('content-container');
    
//             // Inject the content and add a close button
//             contentContainer.innerHTML = htmlContent + '<button id="closeModalButton">×</button>';
//             contentContainer.style.display = 'block';
//             document.getElementById('modalOverlay').style.display = 'block';
    
//             // Add event listener to close button
//             document.getElementById('closeModalButton')?.addEventListener('click', closeModal);

//             // Now load the permission.js script
//             loadScript('/static/permission.js'); // Adjust the path to where permission.js is stored
//         } else {
//             showError(`Page not found: ${response.statusText}`);
//         }
//     } catch (error) {
//         showError(`Network error: ${error.message}`);
//     }
// }

// // Event listener for the 'Load Page' button
// document.getElementById('loadPageButton')?.addEventListener('click', () => {
//     loadPage('/permission');  // Specify the page URL to load
// });

// // Close the modal when the overlay is clicked
// document.getElementById('modalOverlay')?.addEventListener('click', closeModal);



// _______________________________________________
    // Fetch and display user data on page load





    
//________________________________________________________- UPDATE_____________________________________________           


// function attachEditButtonListeners() {
//     const editButtons = document.querySelectorAll(".btn-edit");

//     editButtons.forEach(button => {
//         button.addEventListener("click", function(event) {
//             event.preventDefault(); // Prevent default anchor behavior

//             console.log("Button Element:", this); // Debugging
//             const userId = this.dataset.userid || this.getAttribute("data-userid"); // Fallback
//             console.log("User ID:", userId);
   
//             if (!userId) {
//                 alert("User ID not found!");
//                 return;
//             }

//             const token = localStorage.getItem("access_token");
//             if (!token) {
//                 alert("Authorization token not found!");
//                 return;
//             }

//             // Redirect to the update page and include the token in headers
//             fetch(`/SuperAdmin/update/${userId}`, {
//                 method: "GET",
//                 headers: {
//                     "Authorization": `Bearer ${token}`, // Attach the token here
//                 },
//             })
//             .then(response => {
//                 if (!response.ok) {
//                     return response.text().then(err => {
//                         throw new Error(err || "Failed to load the update page");
//                     });
//                 }
//                 return response.text(); // Assuming the response is HTML content
//             })
//             .then(html => {
//                 // We can either redirect to a new page or inject the HTML into an existing container
//                 // If redirecting to the new page
//                 // window.location.href = `/SuperAdmin/update/${userId}`;
       
//                 window.location.href = "/static/update.html"

//             })
//             .catch(error => {
//                 console.error("Error fetching the update form:", error);
//                 alert("Failed to load the update page: " + error.message);
//             });
//         });
//     });
// }
