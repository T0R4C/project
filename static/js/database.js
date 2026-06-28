document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const papersGrid = document.getElementById('papersGrid');
    const animationContainer = document.getElementById('animationContainer');
    const lottiePlayer = document.getElementById('lottiePlayer');
    const animationMessage = document.getElementById('animationMessage');
    const paginationWrapper = document.getElementById('paginationWrapper');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const currentPageEl = document.getElementById('currentPage');
    const totalCountBadge = document.getElementById('totalCountBadge');

    let currentPage = 1;
    const limit = 21; // 3 columns x 7 rows
    let currentSearch = '';
    let debounceTimer;

    // Lottie URLs
    const ANIM_LOADING = 'https://lottie.host/a98075bc-dd9e-4340-970d-f5e9c05e1eb2/5h75xT3b0b.json'; // Paper searching anim
    const ANIM_EMPTY = 'https://lottie.host/82df0e61-a0a1-43ee-ad71-55dbd39ab010/8N6OaL9Q4N.json'; // Empty ghost/box anim

    // Initial fetch
    fetchPapers(currentPage, currentSearch);

    // Search Input with Debounce
    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        currentSearch = e.target.value.trim();
        debounceTimer = setTimeout(() => {
            currentPage = 1;
            fetchPapers(currentPage, currentSearch);
        }, 500);
    });

    // Pagination Buttons
    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            fetchPapers(currentPage, currentSearch);
        }
    });

    nextBtn.addEventListener('click', () => {
        currentPage++;
        fetchPapers(currentPage, currentSearch);
    });

    async function fetchPapers(page, search) {
        showLoading();
        try {
            const response = await fetch(`/api/papers?page=${page}&limit=${limit}&search=${encodeURIComponent(search)}`);
            const data = await response.json();

            if (!data.success) throw new Error('Failed to load data');

            renderData(data);
        } catch (error) {
            console.error('Error fetching papers:', error);
            showEmpty('Terjadi kesalahan saat memuat data dari server.');
        }
    }

    function renderData(data) {
        // Update counts
        totalCountBadge.textContent = data.total.toLocaleString();
        currentPageEl.textContent = data.page;

        // Pagination buttons state
        prevBtn.disabled = data.page === 1;
        const maxPage = Math.ceil(data.total / data.limit);
        nextBtn.disabled = data.page >= maxPage || data.total === 0;

        if (data.data.length === 0) {
            showEmpty(currentSearch ? 'Pencarian tidak ditemukan.' : 'Belum ada data di database.');
            return;
        }

        // Hide animations
        animationContainer.classList.add('d-none');
        papersGrid.innerHTML = '';
        paginationWrapper.classList.remove('d-none');

        // Render Cards
        data.data.forEach(paper => {
            const abstractPreview = paper.abstract ? 
                (paper.abstract.length > 150 ? paper.abstract.substring(0, 150) + '...' : paper.abstract) : 
                'Tidak ada abstrak tersedia.';

            const card = document.createElement('div');
            card.className = 'col';
            card.innerHTML = `
                <div class="card h-100 paper-card border-0 shadow-sm rounded-4 overflow-hidden bg-white p-4">
                    <div class="d-flex justify-content-between mb-2">
                        <span class="badge bg-light text-primary border border-primary-subtle rounded-pill px-3 py-2">${paper.year || 'N/A'}</span>
                    </div>
                    <h5 class="card-title fw-bold text-dark mb-3 line-clamp-2">${paper.title}</h5>
                    <p class="card-text text-muted small flex-grow-1 line-clamp-4">${abstractPreview}</p>
                    <div class="mt-4 pt-3 border-top d-flex align-items-center">
                        <div class="bg-primary-subtle text-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-journal-text" viewBox="0 0 16 16">
                                <path d="M5 10.5a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5zm0-2a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm0-2a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5zm0-2a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5z"/>
                                <path d="M3 0h10a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2v-1h1v1a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H3a1 1 0 0 0-1 1v1H1V2a2 2 0 0 1 2-2z"/>
                                <path d="M1 5v-.5a.5.5 0 0 1 1 0V5h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1H1zm0 3v-.5a.5.5 0 0 1 1 0V8h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1H1zm0 3v-.5a.5.5 0 0 1 1 0v.5h.5a.5.5 0 0 1 0 1h-2a.5.5 0 0 1 0-1H1z"/>
                            </svg>
                        </div>
                        <div class="overflow-hidden">
                            <h6 class="mb-0 fw-semibold text-dark text-truncate">${paper.authors || 'Unknown Authors'}</h6>
                            <small class="text-muted text-truncate d-block">${paper.venue || 'Unknown Venue'}</small>
                        </div>
                    </div>
                </div>
            `;
            papersGrid.appendChild(card);
        });
        
        // Scroll to top smoothly
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function showLoading() {
        papersGrid.innerHTML = '';
        paginationWrapper.classList.add('d-none');
        animationContainer.classList.remove('d-none');
        lottiePlayer.load(ANIM_LOADING);
        animationMessage.textContent = 'Menarik miliaran pengetahuan dari database...';
    }

    function showEmpty(message) {
        papersGrid.innerHTML = '';
        paginationWrapper.classList.add('d-none');
        animationContainer.classList.remove('d-none');
        lottiePlayer.load(ANIM_EMPTY);
        animationMessage.textContent = message;
    }
});
