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

    function popOutRandomCard() {
        const brokerCards = document.querySelectorAll('.broker-card');
        const randomIndex = Math.floor(Math.random() * brokerCards.length);
        const selectedCard = brokerCards[randomIndex];

        // Add pop-out class
        selectedCard.classList.add('pop-out');

        // Remove pop-out class after animation
        setTimeout(() => {
            selectedCard.classList.remove('pop-out');
        }, 500); // Match the duration of the pop-out animation
    }

    function shuffleBrokerCards() {
        const container = document.getElementById('grid-container');
        const cards = Array.from(container.children);
        // Shuffle the cards array
        for (let i = cards.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [cards[i], cards[j]] = [cards[j], cards[i]]; // Swap
        }
        // Append shuffled cards back to the container
        cards.forEach(card => container.appendChild(card));
    }

    // Set interval to pop out a random card every 45 seconds
    setInterval(popOutRandomCard, 45000); // 45000 ms = 45 seconds

    // Set interval to shuffle cards every 60 seconds
    setInterval(shuffleBrokerCards, 60000); // 60000 ms = 60 seconds

    // Initialize variables for funding visualization
    let maxFunding = 1000000; // Initial max funding goal (adjustable)
    let currentTotal = 0;

    // Function to update the egg fill based on total funding
    function updateEggFill(total) {
        const percentage = Math.min((total / maxFunding) * 100, 100);
        const gradient = document.getElementById('egg-gradient');
        
        // Update gradient stops
        gradient.querySelector('stop:nth-child(1)').setAttribute('offset', `${100 - percentage}%`);
        
        // Format total for display with no decimals and custom currency symbol placement
        const formattedNumber = Math.round(total).toLocaleString('en-US');
        const formattedTotal = '$' + formattedNumber;
        
        // Update total display
        document.getElementById('totalFunding').textContent = formattedTotal;
        
        // Adjust max funding if we exceed it
        if (total > maxFunding) {
            maxFunding = total * 1.5; // Increase max by 50%
        }
    }

    // Handle form submission for funding
    document.getElementById('fundingForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
        const fundingInput = document.getElementById('fundingInput');
        const fundingAmount = parseFloat(fundingInput.value);
        if (!isNaN(fundingAmount) && fundingAmount > 0) {
            currentTotal += fundingAmount; // Update the current total
            updateEggFill(currentTotal); // Update the egg fill
            fundingInput.value = ''; // Clear the input field
        }
    });

    // Initial render
    renderBrokerCards();
});
