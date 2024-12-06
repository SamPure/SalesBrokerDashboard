document.addEventListener('DOMContentLoaded', function() {
    // Use broker data from config.js
    const brokers = brokerData.brokers;

    function createBrokerCard(broker) {
        return `
            <div class="broker-card">
                <h2>${broker.name}</h2>
                <div class="stats">
                    <div class="stat">
                        <span class="label">MTD Submitted</span>
                        <span class="value">${broker.mtdSubmitted}</span>
                    </div>
                    <div class="stat">
                        <span class="label">MTD Funded</span>
                        <span class="value">${broker.mtdFunded}</span>
                    </div>
                    <div class="stat">
                        <span class="label">YTD Funded</span>
                        <span class="value">$${broker.ytdFunded.toLocaleString()}</span>
                    </div>
                </div>
            </div>
        `;
    }

    function updateGridLayout() {
        const container = document.getElementById('grid-container');
        const numBrokers = brokers.length;
        
        // Calculate optimal number of columns based on number of brokers
        let columns;
        if (numBrokers <= 3) columns = numBrokers;
        else if (numBrokers <= 6) columns = 3;
        else if (numBrokers <= 12) columns = 4;
        else if (numBrokers <= 20) columns = 5;
        else columns = 6;

        // Update grid template columns
        container.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
    }

    function renderBrokerCards() {
        const container = document.getElementById('grid-container');
        container.innerHTML = brokers.map(broker => createBrokerCard(broker)).join('');
        updateGridLayout();

        // Set up rotation after cards are rendered
        const brokerCards = document.querySelectorAll('.broker-card');
        let currentIndex = 0;

        function focusNextBroker() {
            brokerCards.forEach(card => card.classList.remove('focused'));
            brokerCards[currentIndex].classList.add('focused');
            currentIndex = (currentIndex + 1) % brokerCards.length;
        }

        // Initial focus
        focusNextBroker();

        // Rotate focus every 10 seconds
        setInterval(focusNextBroker, 10000);
    }

    // Initial render
    renderBrokerCards();
});
