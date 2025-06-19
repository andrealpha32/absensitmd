// Theme management
function initTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const themeIcon = document.querySelector('.theme-toggle i');
    themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
}

// Mobile menu management
function initMobileMenu() {
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const navMenu = document.querySelector('.nav-menu');
    
    menuBtn.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        menuBtn.setAttribute('aria-expanded', 
            menuBtn.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'
        );
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!navMenu.contains(e.target) && !menuBtn.contains(e.target)) {
            navMenu.classList.remove('active');
            menuBtn.setAttribute('aria-expanded', 'false');
        }
    });
}

// Charts theme adaptation
function updateChartsTheme() {
    const theme = document.documentElement.getAttribute('data-theme');
    const chartOptions = {
        light: {
            gridColor: '#e9ecef',
            textColor: '#2c3e50'
        },
        dark: {
            gridColor: '#404040',
            textColor: '#e9ecef'
        }
    };

    const currentTheme = chartOptions[theme];
    
    // Update all Chart.js instances
    if (window.Chart) {
        Chart.instances.forEach(chart => {
            // Update grid lines
            if (chart.options.scales?.x) {
                chart.options.scales.x.grid.color = currentTheme.gridColor;
                chart.options.scales.x.ticks.color = currentTheme.textColor;
            }
            if (chart.options.scales?.y) {
                chart.options.scales.y.grid.color = currentTheme.gridColor;
                chart.options.scales.y.ticks.color = currentTheme.textColor;
            }
            
            // Update title and legend
            if (chart.options.plugins?.title) {
                chart.options.plugins.title.color = currentTheme.textColor;
            }
            if (chart.options.plugins?.legend) {
                chart.options.plugins.legend.labels.color = currentTheme.textColor;
            }
            
            chart.update();
        });
    }
}

// Initialize everything
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initMobileMenu();
    
    // Theme toggle listener
    const themeToggle = document.querySelector('.theme-toggle');
    themeToggle.addEventListener('click', () => {
        toggleTheme();
        updateChartsTheme();
    });
    
    // Handle responsive tables
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-container';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });
});

// Add smooth scrolling for Safari
document.documentElement.style.scrollBehavior = 'smooth';
