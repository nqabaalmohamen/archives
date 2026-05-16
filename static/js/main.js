// Theme Toggle Support
const toggleTheme = () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
};

// Initialize theme from storage
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);

// Document Preview Logic
function previewDocument(url, type) {
    // This could open a modal and load the URL in an iframe or img tag
    window.open(url, '_blank');
}

// Fade in animations on scroll or load
document.addEventListener('DOMContentLoaded', () => {
    const elements = document.querySelectorAll('.fade-in');
    elements.forEach(el => {
        el.style.opacity = '1';
    });
});
