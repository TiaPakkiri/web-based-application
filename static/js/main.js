// Project filtering functionality
function filterProjects() {
    const searchValue = document.getElementById("searchInput")?.value.toLowerCase() || "";
    const projects = document.querySelectorAll(".project-card");

    projects.forEach(project => {
        const title = project.dataset.title?.toLowerCase() || "";
        const campus = project.dataset.campus?.toLowerCase() || "";
        const category = project.dataset.category?.toLowerCase() || "";

        const matchesSearch = title.includes(searchValue);

        if (matchesSearch) {
            project.style.display = "block";
        } else {
            project.style.display = "none";
        }
    });
}

// Event listeners
document.addEventListener("DOMContentLoaded", function() {
    // Add search filtering
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.addEventListener("keyup", filterProjects);
    }

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Success messages
    const alerts = document.querySelectorAll('.alert-success');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.display = 'none';
            });
        }, 5000);
    }
});

// Utility function to format dates
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}
