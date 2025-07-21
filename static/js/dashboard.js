// dashboard.js
window.onload = function() {
    // Example data (replace this with dynamic data from the backend)
    let userName = "John Doe"; // Fetch this from the backend or local storage
    let profilePicture = "https://example.com/profile.jpg"; // You can dynamically set this

    // Set user name and profile picture dynamically
    document.getElementById("user-name").innerText = userName;
    document.getElementById("profile-picture").src = profilePicture;

    // Logout function
    document.getElementById("logout-btn").addEventListener("click", function() {
        // Redirect user to login page or clear session
        window.location.href = "index.html"; // Change the redirection as needed
    });
};
