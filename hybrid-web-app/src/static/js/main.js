// This file contains JavaScript code that adds interactivity to the web pages, handling events and manipulating the DOM.

document.addEventListener('DOMContentLoaded', function() {
    // Initialize filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            filterStudents();
        });
    });

    // Initialize search functionality
    const searchInput = document.getElementById('studentSearch');
    if (searchInput) {
        searchInput.addEventListener('input', filterStudents);
    }
});

function filterStudents() {
    const searchText = document.getElementById('studentSearch').value.toLowerCase();
    const activeFilter = document.querySelector('.filter-btn.active').dataset.status;
    const rows = document.querySelectorAll('.student-row');

    rows.forEach(row => {
        const name = row.querySelector('[data-label="Nama"] span').textContent.toLowerCase();
        const email = row.querySelector('[data-label="Email"]').textContent.toLowerCase();
        const status = row.querySelector('.status-badge').textContent.toLowerCase().trim();
        
        const matchesSearch = name.includes(searchText) || email.includes(searchText);
        const matchesFilter = activeFilter === 'all' || 
                            (activeFilter === 'hadir' && status === 'hadir') ||
                            (activeFilter === 'sakit' && status === 'sakit') ||
                            (activeFilter === 'izin' && status === 'izin') ||
                            (activeFilter === 'absent' && status === 'belum absen');

        row.style.display = matchesSearch && matchesFilter ? '' : 'none';
    });
}

// Additional JavaScript functionality can be added here