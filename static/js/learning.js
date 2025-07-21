// script.js - Cleaned Version without Dark Mode Toggle

document.addEventListener('DOMContentLoaded', function() {
  generateRoadmap();
  smoothScrollToRoadmap(); // Smooth scroll after roadmap generation

  // Ensure the progress bar starts at 0% and is updated after roadmap generation
  updateProgressBar();
});

function generateRoadmap() {
  const skill = document.getElementById('skill').value;
  const duration = document.getElementById('duration').value;

  fetch('/learning/generate-roadmap', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ skill, duration })
  })
  .then(res => res.json())
  .then(data => {
    let html = '';
    const phases = ["Beginner", "Intermediate", "Advanced"];

    phases.forEach((phase, index) => {
      if (data[phase]) {
        html += `
          <div class="phase" style="animation-delay: ${index * 0.2}s">
            <h3>${phase}</h3>
            <ul>
              ${data[phase].map(topic => `
                <li>
                  <input type="checkbox" id="${topic.name}" ${localStorage.getItem(topic.name) === 'true' ? 'checked' : ''}>
                  <label for="${topic.name}">${topic.name}</label>
                  <a href="${topic.resource}" target="_blank" title="Resource link">🔗</a>
                </li>
              `).join('')}
            </ul>
          </div>
        `;
      }
    });

    document.getElementById('roadmap').innerHTML = html;
    addCheckboxListeners();
    updateProgressBar(); // Update progress bar after generating roadmap
  })
  .catch(error => console.error('Error:', error));
}

function addCheckboxListeners() {
  document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', function(e) {
      localStorage.setItem(e.target.id, e.target.checked);
      updateProgressBar();

      // Visual feedback
      if (e.target.checked) {
        e.target.parentElement.style.opacity = '0.7';
        setTimeout(() => {
          e.target.parentElement.style.opacity = '1';
        }, 300);
      }
    });
  });
}

function updateProgressBar() {
  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  const checked = Array.from(checkboxes).filter(cb => cb.checked).length;
  const progress = Math.round((checked / checkboxes.length) * 100);
  const progressBar = document.getElementById('progress');

  // Reset and update progress bar
  if (progressBar) {
    progressBar.style.width = `${progress}%`;
    progressBar.textContent = `${progress}%`;
    progressBar.style.backgroundColor = progress === 100 ? '#4CAF50' : '#2196F3';
  }
}

// Goal Setting
function saveGoal() {
  const goal = document.getElementById('goal').value;
  localStorage.setItem('learningGoal', goal);
  alert('Goal saved!');
}

// Collapsible Content (for roadmap)
document.querySelectorAll('.collapsible').forEach(function(button) {
  button.addEventListener('click', function() {
    this.classList.toggle('active');
    const content = this.nextElementSibling;
    content.style.display = content.style.display === 'block' ? 'none' : 'block';
  });
});
