document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const loadingState = document.getElementById('loading-state');
    const resultsSection = document.getElementById('results-section');
    const cardsContainer = document.getElementById('cards-container');
    const containerCount = document.getElementById('container-count');
    const resetBtn = document.getElementById('reset-btn');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');

    // Drag and Drop Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) handleUpload(files[0]);
    });

    // Click to upload
    browseBtn.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('click', (e) => {
        if (e.target !== browseBtn) fileInput.click();
    });

    fileInput.addEventListener('change', function () {
        if (this.files.length > 0) handleUpload(this.files[0]);
    });

    // Reset view
    resetBtn.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        dropZone.parentElement.classList.remove('hidden');
        fileInput.value = '';
        searchInput.value = '';
    });

    // Search Logic
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });

    async function handleSearch() {
        const query = searchInput.value.trim();
        if (!query) {
            showToast("Please enter a container number to search.");
            return;
        }

        dropZone.parentElement.classList.add('hidden');
        loadingState.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        try {
            const response = await fetch(`/shipment/${encodeURIComponent(query)}`);

            if (response.status === 404) {
                loadingState.classList.add('hidden');
                dropZone.parentElement.classList.remove('hidden');
                showToast(`Container ${query} not found.`);
                return;
            }
            if (!response.ok) {
                throw new Error("Failed to search for container.");
            }

            const data = await response.json();
            // renderResults expects an array
            renderResults([data]);

        } catch (error) {
            console.error('Search error:', error);
            showToast(error.message);
            loadingState.classList.add('hidden');
            dropZone.parentElement.classList.remove('hidden');
        }
    }

    // Upload Logic
    async function handleUpload(file) {
        if (file.type !== 'application/pdf') {
            showToast("Please upload a valid PDF document.");
            return;
        }

        // UI State
        dropZone.parentElement.classList.add('hidden');
        loadingState.classList.remove('hidden');
        resultsSection.classList.add('hidden');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/shipment/upload/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                let errorMessage = "Failed to upload document";
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (e) {
                    errorMessage = await response.text() || errorMessage;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            renderResults(data);
        } catch (error) {
            console.error('Upload error:', error);
            showToast(error.message);
            // Revert UI
            dropZone.parentElement.classList.remove('hidden');
            loadingState.classList.add('hidden');
        }
    }

    function renderResults(shipments) {
        loadingState.classList.add('hidden');

        if (!shipments || shipments.length === 0) {
            showToast("No valid shipping data found in the document");
            dropZone.parentElement.classList.remove('hidden');
            return;
        }

        containerCount.textContent = shipments.length;
        cardsContainer.innerHTML = '';

        shipments.forEach((ship, index) => {
            const card = document.createElement('div');
            card.className = 'card';
            card.style.animationDelay = `${index * 0.15}s`;

            // Format fallback ETA
            const etaFormatted = ship.eta ? ship.eta : "N/A";

            card.innerHTML = `
                <div class="card-header">
                    <div class="container-id">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="2" y="4" width="20" height="16" rx="2" ry="2"></rect>
                            <path d="M10 4v4"></path>
                            <path d="M14 4v4"></path>
                            <path d="M2 10h20"></path>
                        </svg>
                        ${ship.container_number || 'UNKNOWN'}
                    </div>
                    <div class="eta">ETA: ${etaFormatted}</div>
                </div>
                <div class="card-body">
                    <div class="info-group">
                        <span class="info-label">Port of Loading</span>
                        <span class="info-value">⚓ ${ship.port_of_loading || 'N/A'}</span>
                    </div>
                    <div class="info-group">
                        <span class="info-label">Port of Discharge</span>
                        <span class="info-value">🎯 ${ship.port_of_discharge || 'N/A'}</span>
                    </div>
                    <div class="info-group full-width">
                        <span class="info-label">Shipper</span>
                        <span class="info-value">${ship.shipper || 'N/A'}</span>
                    </div>
                    <div class="info-group full-width">
                        <span class="info-label">Consignee</span>
                        <span class="info-value">${ship.consignee || 'N/A'}</span>
                    </div>
                </div>
            `;
            cardsContainer.appendChild(card);
        });

        resultsSection.classList.remove('hidden');
    }

    // Toast Notification System
    function showToast(message) {
        let toast = document.querySelector('.toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.className = 'toast';
            document.body.appendChild(toast);
        }

        toast.textContent = message;
        toast.classList.add('show');

        setTimeout(() => {
            toast.classList.remove('show');
        }, 4000);
    }
});
