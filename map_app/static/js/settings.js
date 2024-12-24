// function for create error label
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.textContent = `Error: ${message}`;
    errorDiv.style.color = 'red';
    document.getElementById('feedback').appendChild(errorDiv);
}

document.addEventListener('DOMContentLoaded', function() {
    // Get credentials from creds.txt and populate the form
    fetch('/api/credentials')
        .then(response => response.json())
        .then(data => {
            document.getElementById('wigle').value = data.wigle;
            document.getElementById('wpasec').value = data.wpasec
            document.getElementById('wifi_pass_map').value = data.wifi_pass_map;
        })
        .catch(error => console.error('Error fetching credentials:', error));

    // Handle form submission
    document.getElementById('credentials-form').addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(this);

        // Send credentials to the server
        fetch('/api/credentials', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(Object.fromEntries(formData))
        })
        .then(response => {
            if (response.ok) {
                document.getElementById('feedback').textContent = 'Saved';
            } else {
                showError('Failed to save credentials');
                throw new Error('Failed to save credentials');
            }
        })
        .catch(error => console.error('Error saving credentials:', error));
        

    });

});
