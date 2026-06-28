document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('searchForm');
    const queryText = document.getElementById('queryText');
    const submitBtn = document.getElementById('submitBtn');
    
    const loadingState = document.getElementById('loadingState');
    const resultsSection = document.getElementById('resultsSection');
    const recommendationsList = document.getElementById('recommendationsList');
    const resultsCount = document.getElementById('resultsCount');
    
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const text = queryText.value.trim();
        if (!text) return;
        
        // Reset UI
        errorAlert.classList.add('d-none');
        resultsSection.classList.add('d-none');
        loadingState.classList.remove('d-none');
        submitBtn.disabled = true;
        
        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Terjadi kesalahan saat memproses permintaan.');
            }
            
            displayResults(data.results);
            
        } catch (error) {
            errorMessage.textContent = error.message;
            errorAlert.classList.remove('d-none');
        } finally {
            loadingState.classList.add('d-none');
            submitBtn.disabled = false;
        }
    });

    function displayResults(papers) {
        recommendationsList.innerHTML = '';
        resultsCount.textContent = `${papers.length} Artikel Ditemukan`;
        
        if (papers.length === 0) {
            recommendationsList.innerHTML = `
                <div class="alert alert-warning border-0 shadow-sm rounded-3">
                    Tidak ada artikel di database yang relevan dengan kueri Anda. Coba kata kunci yang lebih umum.
                </div>
            `;
            resultsSection.classList.remove('d-none');
            return;
        }
        
        papers.forEach(paper => {
            // Determine badge color based on relevance score
            let badgeClass = 'badge-glass';
            if (paper.relevance_score > 30) badgeClass = 'badge-success-glow';
            else if (paper.relevance_score > 15) badgeClass = 'badge-accent-glow';
            
            const card = document.createElement('div');
            card.className = 'magic-card mb-4 animate-slide-up';
            card.innerHTML = `
                <div class="card-body p-4">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span class="badge badge-glass rounded-pill px-3 py-1 mb-2">${paper.year || 'N/A'}</span>
                        <span class="badge ${badgeClass} rounded-pill px-3 py-1">Kecocokan: ${paper.relevance_score}%</span>
                    </div>
                    <h5 class="card-title fw-bold text-gradient mb-3">${paper.title}</h5>
                    <p class="card-text text-secondary mb-4 line-clamp-4">${paper.abstract || 'Tidak ada abstrak.'}</p>
                    <div class="d-flex align-items-center border-top border-secondary pt-3">
                        <div class="rounded-circle d-flex align-items-center justify-content-center me-3 flex-shrink-0" style="width: 40px; height: 40px; background: rgba(255,255,255,0.05); color: #a1a1aa;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" class="bi bi-person-fill" viewBox="0 0 16 16">
                                <path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3Zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>
                            </svg>
                        </div>
                        <div class="overflow-hidden">
                            <h6 class="mb-0 fw-semibold text-primary text-truncate" style="color:#f4f4f5!important;">${paper.authors || 'Unknown Authors'}</h6>
                            <small class="text-secondary text-truncate d-block">${paper.venue || 'Unknown Venue'}</small>
                        </div>
                    </div>
                </div>
            `;
            recommendationsList.appendChild(card);
        });
        
        resultsSection.classList.remove('d-none');
    }
});
