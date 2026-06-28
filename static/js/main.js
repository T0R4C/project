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
            let badgeColor = 'bg-secondary';
            if (paper.relevance_score > 30) badgeColor = 'bg-success';
            else if (paper.relevance_score > 15) badgeColor = 'bg-primary';
            else if (paper.relevance_score > 5) badgeColor = 'bg-info text-dark';
            
            const card = document.createElement('div');
            card.className = 'card border-0 shadow-sm rounded-4 overflow-hidden paper-card bg-white';
            card.innerHTML = `
                <div class="card-body p-4">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span class="badge bg-light text-primary border border-primary-subtle rounded-pill px-3 py-1 mb-2">${paper.year || 'N/A'}</span>
                        <span class="badge ${badgeColor} rounded-pill px-3 py-1">Kecocokan: ${paper.relevance_score}%</span>
                    </div>
                    <h5 class="card-title fw-bold text-dark mb-3">${paper.title}</h5>
                    <p class="card-text text-muted mb-4">${paper.abstract || 'Tidak ada abstrak.'}</p>
                    <div class="d-flex align-items-center border-top pt-3">
                        <div class="bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center me-3 flex-shrink-0" style="width: 40px; height: 40px;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-people" viewBox="0 0 16 16">
                              <path d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8Zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022ZM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0ZM6.936 9.28a5.88 5.88 0 0 0-1.23-.247A7.35 7.35 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816ZM4.92 10A5.493 5.493 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275ZM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0Zm3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z"/>
                            </svg>
                        </div>
                        <div class="overflow-hidden">
                            <h6 class="mb-0 fw-semibold text-dark text-truncate">${paper.authors || 'Unknown Authors'}</h6>
                            <small class="text-muted text-truncate d-block">${paper.venue || 'Unknown Venue'}</small>
                        </div>
                    </div>
                </div>
            `;
            recommendationsList.appendChild(card);
        });
        
        resultsSection.classList.remove('d-none');
    }
});
