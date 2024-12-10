
// const downloadButton = document.getElementById("downloadButton");
// const userInputDiv = document.getElementById("userInput");
// const userIdInput = document.getElementById("userIdInput");
// const submitUserIdButton = document.getElementById("submitUserId");

// // Function to handle the click on the download button
// downloadButton.addEventListener("click", function() {
//     // Show the input box for user ID
//     userInputDiv.style.display = "block";
// });

// // Function to handle the submit of user_id
// submitUserIdButton.addEventListener("click", function() {
//     const userId = userIdInput.value;

//     if (userId) {
//         // Assuming JWT token is stored in localStorage
//         const jwtToken = localStorage.getItem("access_token");

//         if (jwtToken) {
//             // Make the API request to download the CSV file
//             fetch(`/download_single_users_csv?user_id=${userId}`, {
//                 method: "GET",
//                 headers: {
//                     "Authorization": `Bearer ${jwtToken}`,  // Add JWT token to the Authorization header
//                 },
//             })
//             .then(response => {
//                 if (!response.ok) {
//                     throw new Error("Failed to fetch the CSV");
//                 }
//                 return response.blob();  // Get the response as a Blob (file)
//             })
//             .then(blob => {
//                 // Create a download link and trigger download
//                 const url = window.URL.createObjectURL(blob);
//                 const link = document.createElement("a");
//                 link.href = url;
//                 link.setAttribute("download", "user_data.csv");  // Set the file name
//                 document.body.appendChild(link);
//                 link.click();  // Trigger the download
//                 document.body.removeChild(link);  // Clean up the link element
//             })
//             .catch(error => {
//                 console.error("Error:", error);
//             });
//         } else {
//             console.error("JWT token is missing.");
//         }
//     } else {
//         alert("Please enter a valid User ID.");
//     }
// });









        // // Get references to elements
        // const downloadButton = document.getElementById("downloadButton");
        // const modalBackdrop = document.getElementById("modalBackdrop");
        // const userInputModal = document.getElementById("userInputModal");
        // const userIdInput = document.getElementById("userIdInput");
        // const submitUserIdButton = document.getElementById("submitUserId");
        // const closeModalButton = document.getElementById("closeModal");

        // // Function to handle the click on the download button
        // downloadButton.addEventListener("click", function() {
        //     // Show the modal
        //     modalBackdrop.style.display = "block";
        //     userInputModal.style.display = "block";
        // });

        // // Function to close the modal
        // closeModalButton.addEventListener("click", function() {
        //     modalBackdrop.style.display = "none";
        //     userInputModal.style.display = "none";
        // });

        // // Function to handle the submit of user_id
        // submitUserIdButton.addEventListener("click", function() {
        //     const userId = userIdInput.value;

        //     if (userId) {
        //         // Assuming JWT token is stored in localStorage
        //         const jwtToken = localStorage.getItem("access_token");

        //         if (jwtToken) {
        //             // Make the API request to download the CSV file
        //             fetch(`/download_single_users_csv?user_id=${userId}`, {
        //                 method: "GET",
        //                 headers: {
        //                     "Authorization": `Bearer ${jwtToken}`,  // Add JWT token to the Authorization header
        //                 },
        //             })
        //             .then(response => {
        //                 if (!response.ok) {
        //                     // throw new Error("Failed to fetch the CSV");
        //                     alert("this user_id not found",userId)
        //                 }
        //                 return response.blob();  // Get the response as a Blob (file)
        //             })
        //             .then(blob => {
        //                 // Create a download link and trigger download
        //                 const url = window.URL.createObjectURL(blob);
        //                 const link = document.createElement("a");
        //                 link.href = url;
        //                 link.setAttribute("download", "user_data.csv");  // Set the file name
        //                 document.body.appendChild(link);
        //                 link.click();  // Trigger the download
        //                 document.body.removeChild(link);  // Clean up the link element
        //             })
        //             .catch(error => {
        //                 console.error("Error:", error);
        //             });

        //             // Close the modal after submitting
        //             modalBackdrop.style.display = "none";
        //             userInputModal.style.display = "none";
        //         } else {
        //             console.error("JWT token is missing.");
        //         }
        //     } else {
        //         alert("Please enter a valid User ID.");
        //     }
        // });



        // Get references to elements
const downloadButton = document.getElementById("downloadButton");
const modalBackdrop = document.getElementById("modalBackdrop");
const userInputModal = document.getElementById("userInputModal");
const userIdInput = document.getElementById("userIdInput");
const submitUserIdButton = document.getElementById("submitUserId");
const closeModalButton = document.getElementById("closeModal");

// Function to handle the click on the download button
downloadButton.addEventListener("click", function() {
    // Show the modal
    modalBackdrop.style.display = "block";
    userInputModal.style.display = "block";
});

// Function to close the modal
closeModalButton.addEventListener("click", function() {
    modalBackdrop.style.display = "none";
    userInputModal.style.display = "none";
});

// Function to handle the submit of user_id
submitUserIdButton.addEventListener("click", function() {
    const userId = userIdInput.value;

    if (userId) {
        // Assuming JWT token is stored in localStorage
        const jwtToken = localStorage.getItem("access_token");

        if (jwtToken) {
            // Make the API request to download the CSV file
            fetch(`/download_single_users_csv?user_id=${userId}`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${jwtToken}`,  // Add JWT token to the Authorization header
                },
            })
            .then(response => {
                if (!response.ok) {
                    // Handle invalid user_id or other API errors
                    alert(`User with ID ${userId} not found or error occurred. Please try again.`);
                    throw new Error(`Failed to fetch CSV for user_id: ${userId}`);
                }
                return response.blob();  // Get the response as a Blob (file)
            })
            .then(blob => {
                // Create a download link and trigger the download
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement("a");
                link.href = url;
                link.setAttribute("download", "user_data.csv");  // Set the file name
                document.body.appendChild(link);
                link.click();  // Trigger the download
                document.body.removeChild(link);  // Clean up the link element
            })
            .catch(error => {
                console.error("Error:", error);
            });

            // Close the modal after submitting
            modalBackdrop.style.display = "none";
            userInputModal.style.display = "none";
        } else {
            console.error("JWT token is missing.");
        }
    } else {
        alert("Please enter a valid User ID.");
    }
});
