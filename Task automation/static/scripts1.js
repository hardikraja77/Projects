document.getElementById('signupForm').addEventListener('submit', function(e) {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const position = document.getElementById('position').value;

    if (!username || !password || !position) {
        e.preventDefault();
        alert('Please fill in all fields.');
    }
});
