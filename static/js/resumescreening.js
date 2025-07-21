document.getElementById('resume-upload-form').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent form from submitting normally

    let formData = new FormData();
    let resumeFile = document.getElementById('resume-file').files[0];
    formData.append('resume', resumeFile);

    fetch('http://localhost:5000/upload_resume', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.feedback) {
            document.getElementById('resume-feedback').innerHTML = `<p>Feedback: ${data.feedback}</p>`;
        } else {
            document.getElementById('resume-feedback').innerHTML = `<p>Error: ${data.message}</p>`;
        }
    })
    .catch(error => {
        console.error('Error uploading resume:', error);
        document.getElementById('resume-feedback').innerHTML = '<p>Something went wrong. Please try again.</p>';
    });
});
