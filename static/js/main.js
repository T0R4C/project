document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('pdfFile');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const dropArea = document.getElementById('dropArea');
    const submitBtn = document.getElementById('submitBtn');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsArea = document.getElementById('resultsArea');
    const errorMessage = document.getElementById('errorMessage');
    const reportContent = document.getElementById('reportContent');
    const sourcesList = document.getElementById('sourcesList');
    
    // File input change handler
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            const file = e.target.files[0];
            fileNameDisplay.innerHTML = `<span class="fw-bold text-primary">${file.name}</span> (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
        } else {
            fileNameDisplay.textContent = 'Maksimal ukuran file: 10MB';
        }
    });

    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => dropArea.classList.remove('dragover'), false);
    });

    dropArea.addEventListener('drop', (e) => {
        let dt = e.dataTransfer;
        let files = dt.files;
        if(files.length > 0) {
            fileInput.files = files;
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
    });

    // Form Submit
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!fileInput.files[0]) {
            showError('Silakan pilih file PDF terlebih dahulu.');
            return;
        }

        // UI transitions
        uploadForm.classList.add('d-none');
        resultsArea.classList.add('d-none');
        errorMessage.classList.add('d-none');
        loadingIndicator.classList.remove('d-none');

        const formData = new FormData();
        formData.append('pdfFile', fileInput.files[0]);
        formData.append('excludeRefs', document.getElementById('excludeRefs').checked);

        try {
            const response = await fetch('/check', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Terjadi kesalahan saat memproses dokumen.');
            }

            displayResults(data);

        } catch (error) {
            showError(error.message);
        } finally {
            loadingIndicator.classList.add('d-none');
        }
    });

    function displayResults(data) {
        // Hide form, show results
        resultsArea.classList.remove('d-none');
        reportContent.classList.remove('d-none');
        uploadForm.closest('.card').classList.add('d-none'); // Hide the whole upload card for a clean view

        // Populate Score
        const score = data.similarity_percentage;
        const scoreEl = document.getElementById('similarityScore');
        const progressBar = document.getElementById('scoreProgressBar');
        const scoreMessage = document.getElementById('scoreMessage');

        scoreEl.textContent = `${score.toFixed(1)}%`;
        progressBar.style.width = `${score}%`;

        // Color coding based on score
        if (score < 20) {
            scoreEl.style.color = 'var(--success-color)';
            progressBar.className = 'progress-bar bg-success';
            scoreMessage.textContent = 'Dokumen tampaknya orisinal. Kemiripan rendah.';
        } else if (score < 40) {
            scoreEl.style.color = 'var(--warning-color)';
            progressBar.className = 'progress-bar bg-warning';
            scoreMessage.textContent = 'Ditemukan kemiripan sedang. Disarankan untuk meninjau sumber.';
        } else {
            scoreEl.style.color = 'var(--danger-color)';
            progressBar.className = 'progress-bar bg-danger';
            scoreMessage.textContent = 'Kemiripan tinggi terdeteksi! Potensi indikasi plagiarisme besar.';
        }

        // Stats
        document.getElementById('chunksProcessed').textContent = data.processed_chunks;
        document.getElementById('highSimilarityChunks').textContent = data.high_similarity_chunks;

        // Populate Sources
        sourcesList.innerHTML = '';
        if (data.matched_sources && data.matched_sources.length > 0) {
            data.matched_sources.forEach(src => {
                const srcHtml = `
                    <div class="source-card p-4">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="fw-bold mb-0 lh-base text-dark">${src.title}</h6>
                            <span class="source-badge ${getBadgeClass(src.similarity * 100)} ms-3 flex-shrink-0">
                                ${(src.similarity * 100).toFixed(1)}% Cocok
                            </span>
                        </div>
                        <div class="text-muted small mb-2">
                            <i class="bi bi-person me-1"></i> ${src.authors || 'Unknown Authors'}
                        </div>
                        <div class="text-muted small d-flex flex-wrap gap-3">
                            <span><strong>Jurnal/Venue:</strong> ${src.venue || 'N/A'}</span>
                            <span><strong>Tahun:</strong> ${src.year || 'N/A'}</span>
                        </div>
                    </div>
                `;
                sourcesList.innerHTML += srcHtml;
            });
        } else {
            sourcesList.innerHTML = `
                <div class="alert alert-light border text-center p-4">
                    <p class="mb-0 text-muted">Tidak ditemukan kecocokan signifikan dengan sumber akademik yang terindeks.</p>
                </div>
            `;
        }

        // Create a 'Check another file' button at the bottom
        const checkAnotherDiv = document.createElement('div');
        checkAnotherDiv.className = 'text-center mt-5';
        checkAnotherDiv.innerHTML = `
            <button class="btn btn-outline-primary rounded-pill px-4" onclick="location.reload()">
                Periksa Dokumen Lain
            </button>
        `;
        sourcesList.appendChild(checkAnotherDiv);
    }

    function getBadgeClass(score) {
        if (score > 60) return 'bg-danger text-white';
        if (score > 30) return 'bg-warning text-dark';
        return 'bg-info text-dark';
    }

    function showError(message) {
        uploadForm.classList.remove('d-none'); // Show form again so user can retry
        resultsArea.classList.remove('d-none');
        errorMessage.classList.remove('d-none');
        errorMessage.textContent = message;
        reportContent.classList.add('d-none');
    }
});
