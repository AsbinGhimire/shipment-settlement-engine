// BASE TEMPLATE LOGIC
// Navbar shadow on scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar-custom');
    if (navbar) {
        navbar.classList.toggle('shadow-lg', window.scrollY > 10);
    }
});

// Auto-dismiss alerts after Xseconds
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => {
        // Check if bootstrap is defined (it might be loaded via CDN)
        if (typeof bootstrap !== 'undefined') {
            new bootstrap.Alert(alert).close();
        }
    });
}, 9000);
