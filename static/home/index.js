document.addEventListener('DOMContentLoaded', () => {

    const cards = document.querySelectorAll('.feature-card');
    cards.forEach(card => {
        card.addEventListener('click', (e) => {

            if (e.target.classList.contains('button')) {
                e.stopPropagation();
                return;
            }

            const link = card.querySelector('.button').getAttribute('href');
            window.location.href = link;
        });
    });
});
