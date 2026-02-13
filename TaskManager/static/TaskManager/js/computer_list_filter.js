// Filtering for computer list
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.filter-btn').forEach(b => {
            b.classList.remove('btn-primary');
            b.classList.add('btn-outline-primary');
        });
        this.classList.remove('btn-outline-primary');
        this.classList.add('btn-primary');

        const filter = this.getAttribute('data-filter');
        document.querySelectorAll('.computer-card').forEach(card => {
            if (filter === 'all' || card.getAttribute('data-zone') === filter) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    });
});
