// Function to show attendance details in modal
function showDayAttendance(year, month, day) {
    if (!day || day === '') return;
    
    try {
        const formattedDate = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const modal = document.getElementById('attendanceModal');
        const selectedDate = document.getElementById('selectedDate');
        const tableBody = document.getElementById('attendanceTableBody');
        
        // Show loading state
        modal.style.display = 'block';
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <div class="loading-spinner">
                        <i class="fas fa-circle-notch fa-spin"></i>
                        <span>Memuat data...</span>
                    </div>
                </td>
            </tr>`;

        // Make API request
        fetch(`/admin/attendance/${formattedDate}`)
            .then(response => response.json())
            .then(data => {
                if (!data || data.length === 0) {
                    tableBody.innerHTML = `
                        <tr>
                            <td colspan="6" class="text-center">
                                <div class="empty-state">
                                    <i class="fas fa-calendar-times"></i>
                                    <p>Tidak ada data absensi untuk tanggal ini</p>
                                </div>
                            </td>
                        </tr>`;
                    return;
                }

                // Update table with data
                tableBody.innerHTML = data.map(attendance => `
                    <tr>
                        <td>${attendance.student_name || '-'}</td>
                        <td>
                            <span class="badge badge-${(attendance.status || 'unknown').toLowerCase()}">
                                ${attendance.status || 'Tidak diketahui'}
                            </span>
                        </td>
                        <td>${attendance.time_in || '-'}</td>
                        <td>${attendance.activity || '-'}</td>
                        <td class="text-center">
                            ${attendance.photo_path ? 
                                `<button class="btn-photo" 
                                    onclick="confirmPhotoView('/static/${attendance.photo_path}')">
                                    <i class="fas fa-image"></i> Lihat
                                </button>` : 
                                '<span class="no-photo">-</span>'
                            }
                        </td>
                        <td class="text-center">
                            <a href="/admin/student/${attendance.student_id}" 
                               class="btn-action view" 
                               title="Lihat Detail">
                                <i class="fas fa-eye"></i>
                            </a>
                        </td>
                    </tr>
                `).join('');

                // Update displayed date
                selectedDate.textContent = new Date(year, month - 1, day)
                    .toLocaleDateString('id-ID', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                    });
            })
            .catch(error => {
                console.error('Error:', error);
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center">
                            <div class="error-state">
                                <i class="fas fa-exclamation-circle"></i>
                                <p>Gagal memuat data: Silakan coba lagi</p>
                            </div>
                        </td>
                    </tr>`;
            });
    } catch (error) {
        console.error('Error:', error);
        modal.style.display = 'none';
    }
}

// Helper function to get status icon
function getStatusIcon(status) {
    switch (status.toLowerCase()) {
        case 'hadir':
            return 'fa-check-circle';
        case 'izin':
            return 'fa-info-circle';
        case 'sakit':
            return 'fa-hospital';
        default:
            return 'fa-question-circle';
    }
}

// Function to show full-size image
function showFullImage(src) {
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.innerHTML = `
        <div class="image-modal-content">
            <span class="image-modal-close">&times;</span>
            <img src="${src}" alt="Full size image">
        </div>
    `;
    
    document.body.appendChild(modal);
    
    modal.querySelector('.image-modal-close').onclick = function() {
        document.body.removeChild(modal);
    };
    
    modal.onclick = function(e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    };
}

// Close modal when clicking the close button
document.querySelector('.modal .close').onclick = function() {
    document.getElementById('attendanceModal').style.display = 'none';
};

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('attendanceModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
};

function confirmPhotoView(url) {
    const modal = document.createElement('div');
    modal.className = 'photo-modal';
    modal.style.display = 'block'; // Tambahkan ini
    modal.innerHTML = `
        <div class="photo-modal-content">
            <span class="photo-close">&times;</span>
            <img src="${url}" alt="Foto Absensi">
        </div>
    `;
    
    document.body.appendChild(modal);
    
    const closeBtn = modal.querySelector('.photo-close');
    closeBtn.onclick = function() {
        modal.remove();
    };
    
    modal.onclick = function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    };
}
