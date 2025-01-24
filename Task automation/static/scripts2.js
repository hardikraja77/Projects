document.addEventListener("DOMContentLoaded", function () {
    const attendanceForm = document.getElementById('attendanceForm');
    attendanceForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const employeeId = document.getElementById('employeeId').value;
        const date = document.getElementById('date').value;
        const status = document.querySelector('input[name="status"]:checked').value;

        fetch('/submit_attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ employeeId, date, status })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            attendanceForm.reset();
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
