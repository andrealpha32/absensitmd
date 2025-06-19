function initClock() {
    const timeElement = document.querySelector('.digital-clock .time');
    const dateElement = document.querySelector('.digital-clock .date');

    function updateClock() {
        const now = new Date();
        
        // Update time
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        timeElement.textContent = `${hours}:${minutes}:${seconds}`;
        
        // Update date
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        dateElement.textContent = now.toLocaleDateString('id-ID', options);
    }

    setInterval(updateClock, 1000);
    updateClock();
}

document.addEventListener('DOMContentLoaded', initClock);


document.addEventListener('DOMContentLoaded', initClock);
