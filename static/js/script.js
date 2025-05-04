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
    const loadingText = document.getElementById('loading-text');
    const imageViewerContainer = document.getElementById('image-viewer-container');
    const productImage = document.getElementById('product-image');
    const imageLoading = document.getElementById('image-loading');
    const imageLoadingText = document.getElementById('image-loading-text');

    // Add new DOM elements for 3D model viewer
    const modelViewerContainer = document.getElementById('model-viewer-container');
    const modelIframe = document.getElementById('model-iframe');
    const modelLoading = document.getElementById('model-loading');
    const modelLoadingText = document.getElementById('model-loading-text');
    const modelProgress = document.getElementById('model-progress');
    const modelProgressText = document.getElementById('model-progress-text');

    // Current phase
    let currentPhase = 1;
    let shouldAutoScroll = true;

    // Add scroll event listener to detect user scrolling
    chatMessages.addEventListener('scroll', function () {
        // If user has scrolled up, disable auto-scroll
        const isScrolledToBottom = chatMessages.scrollHeight - chatMessages.clientHeight <= chatMessages.scrollTop + 1;
        shouldAutoScroll = isScrolledToBottom;
    });

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

        // Enable auto-scroll when user sends a message
        shouldAutoScroll = true;

        // Add user message to chat
        addMessageToChat('user', message);

        // Clear input
        userInput.value = '';

        // Disable input while waiting for response
        userInput.disabled = true;
        sendButton.disabled = true;

        // Add generating indicator
        const generatingMessageId = addGeneratingIndicator();

        // Check for phase transition messages and show loading if needed
        if (message.toLowerCase() === "appearance design completed" ||
            message.toLowerCase() === "commercial application design finished." ||
            message.toLowerCase() === "generate introduction.") {
            loadingText.textContent = "Generating summary...";
            loadingContainer.style.display = 'flex';
        }
        // Handle image creation request
        else if (message.toLowerCase() === "create image") {
            // Show the main loading container while preparing the transition
            loadingText.textContent = "Generating initial image..."; // Update text here
            loadingContainer.style.display = 'flex';
            // The image-specific loading indicator will show once the viewer appears
        }
        // Handle image design finished request
        else if (currentPhase === 4 && message.toLowerCase() === "image design finished") {
            imageLoadingText.textContent = "Processing final image...";
            imageLoading.style.display = 'flex';
        }
        // Regular image editing in phase 4
        else if (currentPhase === 4) {
            imageLoadingText.textContent = "Editing image...";
            imageLoading.style.display = 'flex';
        }
        // Handle create model request
        else if (message.toLowerCase() === "create model") {
            // Show the main loading container while preparing the transition
            loadingText.textContent = "Preparing to generate 3D model...";
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
                // Hide general loading indicator
                loadingContainer.style.display = 'none';

                // Remove generating indicator
                removeGeneratingIndicator(generatingMessageId);

                // Add assistant response to chat
                if (data.response) {
                    addMessageToChat('assistant', data.response, true); // Add with animation
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
                    void appearanceSummaryContainer.offsetWidth; // Trigger reflow
                    appearanceSummaryContainer.classList.add('fade-in');
                    appearanceSummaryContainer.classList.remove('fade-out');
                }

                if (data.commercial_summary) {
                    // Update commercial summary
                    commercialSummaryContent.innerHTML = marked.parse(data.commercial_summary);
                    commercialSummaryContent.querySelectorAll('pre code').forEach((block) => {
                        Prism.highlightElement(block);
                    });

                    // Fade out appearance summary
                    appearanceSummaryContainer.classList.add('fade-out');
                    appearanceSummaryContainer.classList.remove('fade-in');
                    setTimeout(() => {
                        appearanceSummaryContainer.style.display = 'none';
                        commercialSummaryContainer.style.display = 'block';

                        // Trigger reflow to ensure smooth animation
                        void commercialSummaryContainer.offsetWidth;

                        // Fade in commercial summary
                        commercialSummaryContainer.classList.add('fade-in');
                        commercialSummaryContainer.classList.remove('fade-out');
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
                    commercialSummaryContainer.classList.remove('fade-in');

                    // Wait for fade out to complete, then show product introduction
                    setTimeout(() => {
                        commercialSummaryContainer.style.display = 'none';
                        productIntroContainer.style.display = 'block';

                        // Trigger reflow
                        void productIntroContainer.offsetWidth;

                        // Fade in product introduction
                        productIntroContainer.classList.add('fade-in');
                        productIntroContainer.classList.remove('fade-out');
                    }, 800);
                }

                // Handle image creation action
                if (data.action === "create_image") {
                    createImage();
                }
                // Handle image editing action
                else if (data.action === "edit_image") {
                    editImage(data.edit_prompt);
                }
                // Handle image finalization action
                else if (data.action === "finalize_image") {
                    finalizeImage();
                }
                // Handle 3D model creation
                else if (data.action === "create_model") {
                    createModel();
                }

                // Re-enable input
                userInput.disabled = false;
                sendButton.disabled = false;
                userInput.focus();
            })
            .catch(error => {
                console.error('Error:', error);

                // Hide loading indicators
                loadingContainer.style.display = 'none';
                imageLoading.style.display = 'none';

                // Remove generating indicator
                removeGeneratingIndicator(generatingMessageId);

                addMessageToChat('assistant', 'Sorry, there was an error processing your request. Please try again.');

                // Re-enable input
                userInput.disabled = false;
                sendButton.disabled = false;
                userInput.focus();
            });
    }

    // Function to create the initial image
    function createImage() {
        // Show image loading indicator
        imageLoadingText.textContent = "Generating initial image...";
        imageLoading.style.display = 'flex';

        // Keep the main loading container visible during the entire process
        loadingText.textContent = "Generating initial image...";
        loadingContainer.style.display = 'flex';

        // Transition from product intro to image viewer
        productIntroContainer.classList.add('fade-out');
        productIntroContainer.classList.remove('fade-in');

        setTimeout(() => {
            productIntroContainer.style.display = 'none';
            // Don't show image viewer immediately
            // imageViewerContainer.style.display = 'block'; 

            // Call API to create image
            fetch('/create-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
                .then(response => response.json())
                .then(data => {
                    // Only hide loading indicators after successful image creation
                    loadingContainer.style.display = 'none';
                    imageLoading.style.display = 'none';

                    if (data.success) {
                        // Set the image source first
                        productImage.src = data.image_path;

                        // Now show and fade in the image viewer container
                        imageViewerContainer.style.display = 'block';
                        void imageViewerContainer.offsetWidth; // Trigger reflow
                        imageViewerContainer.classList.add('fade-in');
                        imageViewerContainer.classList.remove('fade-out');

                        // Animate the image appearance
                        productImage.classList.add('image-appear');

                        // Add system message to chat
                        addMessageToChat('assistant', 'Image has been created. You can now provide instructions to edit it, or type "image design finished" when you\'re done.', true);
                    } else {
                        // Show error message
                        addMessageToChat('assistant', `Error creating image: ${data.message}`, true);
                        // If creation failed, maybe hide the image viewer or show a placeholder?
                        // For now, just keep it hidden if it wasn't shown yet
                        imageViewerContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    loadingContainer.style.display = 'none';
                    imageLoading.style.display = 'none';
                    addMessageToChat('assistant', 'There was an error generating the image. Please try again.', true);
                    // Keep viewer hidden on error
                    imageViewerContainer.style.display = 'none';
                });
        }, 800);
    }

    // Function to edit the image
    function editImage(prompt) {
        // Show image loading
        imageLoadingText.textContent = "Editing image...";
        imageLoading.style.display = 'flex';

        // Call API to edit image
        fetch('/edit-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt
            }),
        })
            .then(response => response.json())
            .then(data => {
                // Hide image loading indicator
                imageLoading.style.display = 'none';

                if (data.success) {
                    // Remove current image appear class
                    productImage.classList.remove('image-appear');

                    // Force reflow
                    void productImage.offsetWidth;

                    // Update image source and add animation
                    productImage.src = data.image_path;
                    productImage.classList.add('image-appear');

                    // Add system message to chat
                    if (data.text_response) {
                        addMessageToChat('assistant', data.text_response, true);
                    } else {
                        addMessageToChat('assistant', 'Image has been edited according to your instructions.', true);
                    }
                } else {
                    // Show error message
                    addMessageToChat('assistant', `Error editing image: ${data.message}`, true);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                imageLoading.style.display = 'none';
                addMessageToChat('assistant', 'There was an error editing the image. Please try again.', true);
            });
    }

    // Function to finalize the image
    function finalizeImage() {
        // Show image loading
        imageLoadingText.textContent = "Finalizing high resolution image...";
        imageLoading.style.display = 'flex';

        // Call API to finalize image
        fetch('/finalize-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
            .then(response => response.json())
            .then(data => {
                // Hide image loading indicator
                imageLoading.style.display = 'none';

                if (data.success) {
                    // Remove current image appear class
                    productImage.classList.remove('image-appear');

                    // Force reflow
                    void productImage.offsetWidth;

                    // Update image source and add animation
                    productImage.src = data.image_path + '?' + new Date().getTime(); // Add timestamp to prevent caching
                    productImage.classList.add('image-appear');

                    // Add system message to chat
                    addMessageToChat('assistant', 'Final high-resolution image has been created. Your product design is now complete! Type "create model" to generate a 3D model of your product.', true);

                    // Show the model reminder
                    const modelReminder = document.getElementById('model-reminder');
                    if (modelReminder) {
                        modelReminder.style.display = 'block';
                        // Auto-hide the reminder after 8 seconds
                        setTimeout(() => {
                            modelReminder.style.display = 'none';
                        }, 8000);
                    }
                } else {
                    // Show error message
                    addMessageToChat('assistant', `Error finalizing image: ${data.message}`, true);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                imageLoading.style.display = 'none';
                addMessageToChat('assistant', 'There was an error finalizing the image. Please try again.', true);
            });
    }

    // Function to create 3D model
    function createModel() {
        // Show model loading indicator
        modelLoadingText.textContent = "Generating 3D model...";
        modelLoading.style.display = 'flex';
        modelProgress.style.width = "0%";
        modelProgressText.textContent = "0%";

        // Keep the main loading container visible during the entire process
        loadingText.textContent = "Generating 3D model...";
        loadingContainer.style.display = 'flex';

        // Transition from image viewer to model viewer
        imageViewerContainer.classList.add('fade-out');
        imageViewerContainer.classList.remove('fade-in');

        setTimeout(() => {
            imageViewerContainer.style.display = 'none';
            // Don't show model viewer immediately, show only after model is created
            // modelViewerContainer.style.display = 'block'; 

            // Call API to create 3D model task
            fetch('/create-model', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Store the task ID for polling progress
                        const taskId = data.task_id;
                        // Start polling for task progress
                        pollModelProgress(taskId);
                    } else {
                        // Hide loading indicators on error
                        loadingContainer.style.display = 'none';
                        modelLoading.style.display = 'none';

                        // Show error message
                        addMessageToChat('assistant', `Error creating 3D model task: ${data.message}`, true);
                        // Revert to image viewer
                        imageViewerContainer.style.display = 'block';
                        void imageViewerContainer.offsetWidth; // Trigger reflow
                        imageViewerContainer.classList.add('fade-in');
                        imageViewerContainer.classList.remove('fade-out');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    loadingContainer.style.display = 'none';
                    modelLoading.style.display = 'none';
                    addMessageToChat('assistant', 'There was an error starting the 3D model generation. Please try again.', true);
                    // Revert to image viewer on error
                    imageViewerContainer.style.display = 'block';
                    void imageViewerContainer.offsetWidth; // Trigger reflow
                    imageViewerContainer.classList.add('fade-in');
                    imageViewerContainer.classList.remove('fade-out');
                });
        }, 800);
    }

    // Function to poll for model generation progress
    function pollModelProgress(taskId) {
        let lastProgress = 0;

        // Function to check progress of the task
        function checkProgress() {
            fetch(`/get-model-progress?task_id=${taskId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const progress = data.progress;
                        modelProgress.style.width = `${progress}%`;
                        modelProgressText.textContent = `${Math.round(progress)}%`;

                        // Update message if progress has changed significantly
                        if (progress - lastProgress >= 10) {
                            lastProgress = progress;
                            addMessageToChat('assistant', `3D model generation in progress: ${Math.round(progress)}% complete`, true);
                        }

                        // If the model is complete, download it
                        if (data.status === "SUCCEEDED") {
                            modelLoadingText.textContent = "Downloading 3D model...";
                            downloadModel(taskId);
                            return; // Stop polling
                        }
                        // If the model generation failed, show error
                        else if (data.status === "FAILED" || data.status === "CANCELLED") {
                            loadingContainer.style.display = 'none';
                            modelLoading.style.display = 'none';
                            addMessageToChat('assistant', `The 3D model generation ${data.status.toLowerCase()}. Please try again.`, true);

                            // Revert to image viewer
                            imageViewerContainer.style.display = 'block';
                            void imageViewerContainer.offsetWidth;
                            imageViewerContainer.classList.add('fade-in');
                            imageViewerContainer.classList.remove('fade-out');
                            return; // Stop polling
                        }

                        // Continue polling
                        setTimeout(checkProgress, 5000);
                    } else {
                        // Error getting progress, try again
                        setTimeout(checkProgress, 5000);
                    }
                })
                .catch(error => {
                    console.error('Error polling progress:', error);
                    // Try again after delay
                    setTimeout(checkProgress, 5000);
                });
        }

        // Start polling
        checkProgress();
    }

    // Function to download the completed model
    function downloadModel(taskId) {
        fetch('/download-model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task_id: taskId
            })
        })
            .then(response => response.json())
            .then(data => {
                // Hide loading indicators
                loadingContainer.style.display = 'none';
                modelLoading.style.display = 'none';

                if (data.success) {
                    // Set the iframe source to the model viewer page
                    modelIframe.src = `/view-model/Product 3D Model.glb`;

                    // Now show and fade in the model viewer container
                    modelViewerContainer.style.display = 'block';
                    void modelViewerContainer.offsetWidth; // Trigger reflow
                    modelViewerContainer.classList.add('fade-in');
                    modelViewerContainer.classList.remove('fade-out');

                    // Add system message to chat
                    addMessageToChat('assistant', 'The 3D model has been created. You can now interact with it in the viewer.', true);
                } else {
                    // Show error message
                    addMessageToChat('assistant', `Error downloading 3D model: ${data.message}`, true);
                    // Revert to image viewer
                    imageViewerContainer.style.display = 'block';
                    void imageViewerContainer.offsetWidth; // Trigger reflow
                    imageViewerContainer.classList.add('fade-in');
                    imageViewerContainer.classList.remove('fade-out');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                loadingContainer.style.display = 'none';
                modelLoading.style.display = 'none';
                addMessageToChat('assistant', 'There was an error downloading the 3D model. Please try again.', true);
                // Revert to image viewer on error
                imageViewerContainer.style.display = 'block';
                void imageViewerContainer.offsetWidth; // Trigger reflow
                imageViewerContainer.classList.add('fade-in');
                imageViewerContainer.classList.remove('fade-out');
            });
    }

    // Function to add a temporary generating message
    function addGeneratingIndicator() {
        const messageId = `generating-${Date.now()}`;
        const messageDiv = document.createElement('div');
        messageDiv.id = messageId;
        messageDiv.className = 'message assistant generating';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = 'Generating...';

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Only scroll if we're already at the bottom
        if (shouldAutoScroll) {
            scrollToBottom();
        }
        return messageId;
    }

    // Function to remove the generating message
    function removeGeneratingIndicator(messageId) {
        const generatingMessage = document.getElementById(messageId);
        if (generatingMessage) {
            generatingMessage.remove();
        }
    }

    // Function to add message to chat
    function addMessageToChat(sender, content, animate = false) {
        // Create message container
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        if (animate) {
            messageDiv.classList.add('new-message');
        }

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

        // Only scroll if it's a user message or we're already at the bottom
        if (sender === 'user' || shouldAutoScroll) {
            scrollToBottom();
        }

        // Trigger animation if requested
        if (animate) {
            // Force reflow to ensure animation runs
            void messageDiv.offsetWidth;
            messageDiv.classList.remove('new-message');
        }
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function updatePhaseIndicator() {
        switch (currentPhase) {
            case 1:
                phaseLabel.textContent = "Phase 1: Appearance Design";
                break;
            case 2:
                phaseLabel.textContent = "Phase 2: Commercial Application";
                break;
            case 2.5:
                phaseLabel.textContent = "Phase 2.5: Introduction Preparation";
                break;
            case 3:
                phaseLabel.textContent = "Phase 3: Product Introduction";
                break;
            case 4:
                phaseLabel.textContent = "Phase 4: Image Design";
                break;
            case 5:
                phaseLabel.textContent = "Phase 5: 3D Model Creation";
                break;
            default:
                phaseLabel.textContent = "Product Design Assistant";
        }
    }
}); 