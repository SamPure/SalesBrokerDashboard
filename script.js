document.addEventListener('DOMContentLoaded', function() {
    const brokerCards = document.querySelectorAll('.broker-card');
    let currentIndex = 0;

    function focusNextBroker() {
        // Remove focus from all cards
        brokerCards.forEach(card => {
            card.classList.remove('focused');
            card.style.transform = 'scale(1)';
        });
        
        // Add focus to current card
        const currentCard = brokerCards[currentIndex];
        currentCard.classList.add('focused');
        currentCard.style.transform = 'scale(1.05)';
        
        // Smooth scroll to the focused card if it's not fully visible
        const cardRect = currentCard.getBoundingClientRect();
        const isFullyVisible = (
            cardRect.top >= 0 &&
            cardRect.left >= 0 &&
            cardRect.bottom <= window.innerHeight &&
            cardRect.right <= window.innerWidth
        );

        if (!isFullyVisible) {
            currentCard.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }
        
        // Update index for next iteration
        currentIndex = (currentIndex + 1) % brokerCards.length;
    }

    // Initial focus
    focusNextBroker();

    // Rotate focus every 10 seconds
    setInterval(focusNextBroker, 10000);

    // Add click handler to manually focus cards
    brokerCards.forEach((card, index) => {
        card.addEventListener('click', () => {
            currentIndex = index;
            focusNextBroker();
        });
    });
});
