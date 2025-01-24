document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting via the browser

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;
    const errorMessage = document.getElementById('error-message');

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}&role=${encodeURIComponent(role)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = data.redirect; // Redirect to the appropriate dashboard
        } else {
            errorMessage.textContent = data.message; // Display error message
        }
    })
    .catch(error => {
        errorMessage.textContent = 'An error occurred. Please try again.';
        console.error('Error:', error);
    });
});
