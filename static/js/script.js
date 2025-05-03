document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const phaseLabel = document.getElementById('phase-label');
    const appearanceSummaryContent = document.getElementById('appearance-summary-content');
    const commercialSummaryContent = document.getElementById('commercial-summary-content');
    const appearanceSummaryContainer = document.getElementById('appearance-summary-container');
    const commercialSummaryContainer = document.getElementById('commercial-summary-container');
    const productIntroContainer = document.getElementById('product-intro-container');
    const productIntroContent = document.getElementById('product-intro-content');
    const loadingContainer = document.getElementById('loading-container');

    // Current phase
    let currentPhase = 1;

    // Send message when Enter key is pressed (without Shift)
    userInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Send message when send button is clicked
    sendButton.addEventListener('click', sendMessage);

    // Function to send message
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessageToChat('user', message);

        // Clear input
        userInput.value = '';

        // Disable input while waiting for response
        userInput.disabled = true;
        sendButton.disabled = true;

        // Check for phase transition messages and show loading if needed
        if (message.toLowerCase() === "appearance design completed" ||
            message.toLowerCase() === "commercial application design finished." ||
            message.toLowerCase() === "generate introduction.") {
            loadingContainer.style.display = 'flex';
        }

        // Send message to server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message
            }),
        })
            .then(response => response.json())
            .then(data => {
                // Hide loading indicator
                loadingContainer.style.display = 'none';

                // Add assistant response to chat
                if (data.response) {
                    addMessageToChat('assistant', data.response);
                }

                // Update phase if changed
                if (data.phase && data.phase !== currentPhase) {
                    currentPhase = data.phase;
                    updatePhaseIndicator();
                }

                // Handle phase-specific updates
                if (data.appearance_summary) {
                    // Update appearance summary
                    appearanceSummaryContent.innerHTML = marked.parse(data.appearance_summary);
                    appearanceSummaryContent.querySelectorAll('pre code').forEach((block) => {
                        Prism.highlightElement(block);
                    });

                    // Show appearance summary container
                    appearanceSummaryContainer.style.display = 'block';
                }

                if (data.commercial_summary) {
                    // Update commercial summary
                    commercialSummaryContent.innerHTML = marked.parse(data.commercial_summary);
                    commercialSummaryContent.querySelectorAll('pre code').forEach((block) => {
                        Prism.highlightElement(block);
                    });

                    // Fade out appearance summary
                    appearanceSummaryContainer.classList.add('fade-out');
                    setTimeout(() => {
                        appearanceSummaryContainer.style.display = 'none';
                        commercialSummaryContainer.style.display = 'block';

                        // Trigger reflow to ensure smooth animation
                        void commercialSummaryContainer.offsetWidth;

                        // Fade in commercial summary
                        commercialSummaryContainer.classList.add('fade-in');
                    }, 800);
                }

                if (data.product_introduction) {
                    // Show product introduction with fade effect
                    productIntroContent.innerHTML = marked.parse(data.product_introduction);
                    productIntroContent.querySelectorAll('pre code').forEach((block) => {
                        Prism.highlightElement(block);
                    });

                    // Fade out commercial summary
                    commercialSummaryContainer.classList.add('fade-out');

                    // Wait for fade out to complete, then show product introduction
                    setTimeout(() => {
                        commercialSummaryContainer.style.display = 'none';
                        productIntroContainer.style.display = 'block';

                        // Trigger reflow
                        void productIntroContainer.offsetWidth;

                        // Fade in product introduction
                        productIntroContainer.classList.add('fade-in');
                    }, 800);
                }

                // Re-enable input
                userInput.disabled = false;
                sendButton.disabled = false;
                userInput.focus();
            })
            .catch(error => {
                console.error('Error:', error);

                // Hide loading indicator
                loadingContainer.style.display = 'none';

                addMessageToChat('assistant', 'Sorry, there was an error processing your request. Please try again.');

                // Re-enable input
                userInput.disabled = false;
                sendButton.disabled = false;
                userInput.focus();
            });
    }

    // Function to add message to chat
    function addMessageToChat(sender, content) {
        // Create message container
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        // Create message content
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // Parse markdown if it's from the assistant
        if (sender === 'assistant') {
            contentDiv.innerHTML = marked.parse(content);
            // Apply syntax highlighting to code blocks
            contentDiv.querySelectorAll('pre code').forEach((block) => {
                Prism.highlightElement(block);
            });
        } else {
            contentDiv.textContent = content;
        }

        // Add content to message
        messageDiv.appendChild(contentDiv);

        // Add message to chat
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to update phase indicator
    function updatePhaseIndicator() {
        switch (currentPhase) {
            case 1:
                phaseLabel.textContent = 'Phase 1: Appearance Design';
                break;
            case 2:
                phaseLabel.textContent = 'Phase 2: Commercial Application Design';
                break;
            case 2.5:
                phaseLabel.textContent = 'Phase 2.5: Prepare for Introduction';
                break;
            case 3:
                phaseLabel.textContent = 'Phase 3: Product Introduction';
                break;
            default:
                phaseLabel.textContent = 'Product Design Process';
        }
    }
}); 