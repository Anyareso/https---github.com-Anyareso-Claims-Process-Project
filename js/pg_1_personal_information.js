document.querySelector('.btn-next').addEventListener('click', function() {
    const sectionUrl = this.getAttribute('data-section');
    if (sectionUrl) {
        window.location.href = sectionUrl;
    }
});