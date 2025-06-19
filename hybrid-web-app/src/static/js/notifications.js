// Handle notifications
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        // Remove alert after 5 seconds
        setTimeout(() => {
            alert.remove();
        }, 5000);

        // Optional: Add close button functionality
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.className = 'alert-close';
        closeButton.onclick = () => alert.remove();
        alert.appendChild(closeButton);
    });
});
