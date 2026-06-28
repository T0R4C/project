document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const papersGrid = document.getElementById('papersGrid');
    const animationContainer = document.getElementById('animationContainer');
    const lottiePlayer = document.getElementById('lottiePlayer');
    const animationMessage = document.getElementById('animationMessage');
    
    const currentRange = document.getElementById('currentRange');
    const totalPapers = document.getElementById('totalPapers');
    const paginationWrapper = document.getElementById('paginationWrapper');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const currentPageSpan = document.getElementById('currentPage');
    
    // Also update the header badge if it exists
    const totalCountBadge = document.getElementById('totalCountBadge');

    let currentPage = 1;
    let currentLimit = 21; // 3x7 grid
    let currentQuery = '';
    let totalResults = 0;
    
    // Debounce timer for search
    let searchTimeout = null;

    // Initial load
    fetchData();

    // Event Listeners
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        currentQuery = e.target.value.trim();
        
        searchTimeout = setTimeout(() => {
            currentPage = 1;
            fetchData();
        }, 500); // 500ms debounce
    });

    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            fetchData();
        }
    });

    nextBtn.addEventListener('click', () => {
        const maxPage = Math.ceil(totalResults / currentLimit);
        if (currentPage < maxPage) {
            currentPage++;
            fetchData();
        }
    });

    function showAnimation(type) {
        papersGrid.innerHTML = '';
        paginationWrapper.classList.add('d-none');
        animationContainer.classList.remove('d-none');
        
        if (type === 'loading') {
            lottiePlayer.load('https://lottie.host/a98075bc-dd9e-4340-970d-f5e9c05e1eb2/5h75xT3b0b.json');
            animationMessage.textContent = 'Memuat Jurnal...';
            animationMessage.className = 'fw-bold text-gradient-accent mt-3';
        } else if (type === 'empty') {
            lottiePlayer.load('https://lottie.host/9e4d0b43-22cf-4b10-8b65-6901cd991e23/C9JqP4c8aR.json');
            animationMessage.textContent = 'Jurnal Tidak Ditemukan';
            animationMessage.className = 'fw-bold text-muted mt-3';
        } else if (type === 'error') {
            lottiePlayer.load('https://lottie.host/9e4d0b43-22cf-4b10-8b65-6901cd991e23/C9JqP4c8aR.json'); // Fallback to empty for now
            animationMessage.textContent = 'Gagal memuat data dari server';
            animationMessage.className = 'fw-bold text-danger mt-3';
        }
    }

    async function fetchData() {
        showAnimation('loading');
        
        try {
            const url = `/api/papers?page=${currentPage}&limit=${currentLimit}&search=${encodeURIComponent(currentQuery)}`;
            const response = await fetch(url);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Terjadi kesalahan saat memuat data');
            }
            
            totalResults = data.total;
            totalPapers.textContent = totalResults.toLocaleString();
            if (totalCountBadge) totalCountBadge.textContent = totalResults.toLocaleString();
            
            if (totalResults === 0) {
                showAnimation('empty');
                currentRange.textContent = '0-0';
                return;
            }

            animationContainer.classList.add('d-none');
            renderPapers(data.data);
            updatePagination();
            paginationWrapper.classList.remove('d-none');
            
        } catch (error) {
            console.error('Fetch error:', error);
            showAnimation('error');
            currentRange.textContent = '0-0';
        }
    }

    function renderPapers(papers) {
        papersGrid.innerHTML = '';
        papers.forEach((paper, index) => {
            const card = document.createElement('div');
            card.className = 'col-md-6 col-lg-4 mb-4';
            
            // Add staggered animation delay
            const delay = (index % 6) * 100;
            
            card.innerHTML = `
                <div class="magic-card h-100 animate-slide-up" style="animation-delay: ${delay}ms;">
                    <div class="card-body p-4 d-flex flex-column h-100">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <span class="badge badge-glass rounded-pill px-3 py-1">${paper.year || 'N/A'}</span>
                            <a href="https://semanticscholar.org/paper/${paper.paper_id}" target="_blank" class="text-decoration-none" style="color: #6366f1;" title="Buka di Semantic Scholar">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-box-arrow-up-right" viewBox="0 0 16 16">
                                  <path fill-rule="evenodd" d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5z"/>
                                  <path fill-rule="evenodd" d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0v-5z"/>
                                </svg>
                            </a>
                        </div>
                        <h5 class="card-title fw-bold text-gradient mb-3 line-clamp-2" title="${paper.title}">${paper.title}</h5>
                        <p class="card-text text-secondary mb-4 flex-grow-1 line-clamp-4">${paper.abstract || 'Tidak ada deskripsi abstrak untuk artikel ini.'}</p>
                        <div class="d-flex align-items-center border-top border-secondary pt-3 mt-auto">
                            <div class="rounded-circle d-flex align-items-center justify-content-center me-3 flex-shrink-0" style="width: 36px; height: 36px; background: rgba(255,255,255,0.05); color: #a1a1aa;">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-person-lines-fill" viewBox="0 0 16 16">
                                  <path d="M6 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6zm-5 6s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H1zM11 3.5a.5.5 0 0 1 .5-.5h4a.5.5 0 0 1 0 1h-4a.5.5 0 0 1-.5-.5zm.5 2.5a.5.5 0 0 0 0 1h4a.5.5 0 0 0 0-1h-4zm2 3a.5.5 0 0 0 0 1h2a.5.5 0 0 0 0-1h-2zm0 3a.5.5 0 0 0 0 1h2a.5.5 0 0 0 0-1h-2z"/>
                                </svg>
                            </div>
                            <div class="overflow-hidden">
                                <h6 class="mb-0 fw-semibold text-primary text-truncate" style="color:#f4f4f5!important;" title="${paper.authors || 'Unknown Authors'}">${paper.authors || 'Unknown Authors'}</h6>
                                <small class="text-secondary text-truncate d-block" title="${paper.venue || 'Unknown Venue'}">${paper.venue || 'Unknown Venue'}</small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            papersGrid.appendChild(card);
        });
    }

    function updatePagination() {
        const start = (currentPage - 1) * currentLimit + 1;
        const end = Math.min(currentPage * currentLimit, totalResults);
        
        currentRange.textContent = `${start}-${end}`;
        if (currentPageSpan) currentPageSpan.textContent = currentPage;
        
        prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = end >= totalResults;
    }
});
