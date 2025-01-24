document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('attendanceForm');

    form.addEventListener('submit', function(event) {
        // Prevent default form submission
        event.preventDefault();

        // Validate form fields
        if (validateForm()) {
            // If validation passes, submit the form
            form.submit();
        }
    });

    function validateForm() {
        const employeeId = document.getElementById('employeeId').value.trim();
        const departmentId = document.getElementById('departmentId').value.trim();
        const date = document.getElementById('date').value;
        const status = document.querySelector('input[name="status"]:checked');

        if (employeeId === '') {
            alert('Please enter Employee ID.');
            return false;
        }

        if (departmentId === '') {
            alert('Please enter Department ID.');
            return false;
        }

        if (date === '') {
            alert('Please select a date.');
            return false;
        }

        if (!status) {
            alert('Please select a status.');
            return false;
        }

        return true;
    }
});
