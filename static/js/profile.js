function saveProfile() {
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;

    // Prepare the data to be sent to the server
    const data = {
        name: name,
        email: email
    };

    // Make an AJAX request to the backend to update the profile
    fetch('/update_profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Profile updated successfully!");
        } else {
            alert("Error updating profile.");
        }
    })
    .catch((error) => {
        console.error("Error:", error);
        alert("Something went wrong. Please try again.");
    });
}
