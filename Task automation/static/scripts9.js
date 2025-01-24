document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('assignTaskForm');
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(form);
        const data = {
            taskName: formData.get('taskName'),
            assignTo: formData.get('assignTo'),
            departmentId: formData.get('departmentId'),
            deadlineDate: formData.get('deadlineDate')
        };

        fetch('/submit_task1', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            alert(result.message || result.error);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
