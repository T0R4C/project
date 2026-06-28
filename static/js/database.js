/* Scholar AI — database.js */

(function () {
  'use strict';

  const searchInput  = document.getElementById('searchInput');
  const papersGrid   = document.getElementById('papersGrid');
  const stateLoading = document.getElementById('stateLoading');
  const stateEmpty   = document.getElementById('stateEmpty');
  const stateError   = document.getElementById('stateError');
  const totalBadge   = document.getElementById('totalBadge');
  const totalText    = document.getElementById('totalText');
  const rangeText    = document.getElementById('rangeText');
  const paginationBar = document.getElementById('paginationBar');
  const prevBtn      = document.getElementById('prevBtn');
  const nextBtn      = document.getElementById('nextBtn');
  const pageDots     = document.getElementById('pageDots');
  const dbYearFrom   = document.getElementById('dbYearFrom');
  const dbYearTo     = document.getElementById('dbYearTo');

  let page   = 1;
  const limit = 18;
  let total  = 0;
  let query  = '';
  let yFrom  = null;
  let yTo    = null;
  let debounceTimer = null;

  // ── Populate year dropdowns ──────────────────────────────
  const curYear = new Date().getFullYear();
  for (let y = curYear; y >= 1990; y--) {
    dbYearFrom.add(new Option(y, y));
    dbYearTo.add(new Option(y, y));
  }

  // ── Events ───────────────────────────────────────────────
  searchInput.addEventListener('input', e => {
    clearTimeout(debounceTimer);
    query = e.target.value.trim();
    debounceTimer = setTimeout(() => { page = 1; fetchData(); }, 450);
  });

  dbYearFrom.addEventListener('change', () => { yFrom = dbYearFrom.value ? +dbYearFrom.value : null; page = 1; fetchData(); });
  dbYearTo.addEventListener('change', () => { yTo = dbYearTo.value ? +dbYearTo.value : null; page = 1; fetchData(); });
  prevBtn.addEventListener('click', () => { if (page > 1) { page--; fetchData(); } });
  nextBtn.addEventListener('click', () => { const max = Math.ceil(total / limit); if (page < max) { page++; fetchData(); } });

  // ── Initial Load ─────────────────────────────────────────
  fetchData();

  async function fetchData() {
    setStates('loading');
    try {
      let url = `/api/papers?page=${page}&limit=${limit}&search=${encodeURIComponent(query)}`;
      if (yFrom) url += `&year_from=${yFrom}`;
      if (yTo)   url += `&year_to=${yTo}`;

      const res  = await fetch(url);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Error');

      total = data.total;

      const totalNum = total.toLocaleString('id-ID');
      if (totalBadge) totalBadge.textContent = `${totalNum} artikel`;
      if (totalText)  totalText.textContent  = totalNum;

      if (total === 0) { setStates('empty'); return; }

      renderSkeletons();
      await new Promise(r => setTimeout(r, 150)); // brief pause for UX
      renderPapers(data.data);
      renderPagination();
      setStates('data');

    } catch (err) {
      console.error(err);
      setStates('error');
    }
  }

  function setStates(state) {
    stateLoading.classList.toggle('d-none', state !== 'loading');
    stateEmpty.classList.toggle('d-none',   state !== 'empty');
    stateError.classList.toggle('d-none',   state !== 'error');
    papersGrid.classList.toggle('d-none',   state !== 'data');
    paginationBar.classList.toggle('d-none', state !== 'data');
  }

  function renderSkeletons() {
    papersGrid.innerHTML = '';
    papersGrid.classList.remove('d-none');
    for (let i = 0; i < limit; i++) {
      const col = document.createElement('div');
      col.className = 'col-md-6 col-lg-4';
      col.innerHTML = `
        <div class="magic-card p-4" style="min-height:220px;">
          <div class="skeleton mb-3" style="height:16px;width:60%;"></div>
          <div class="skeleton mb-2" style="height:20px;width:100%;"></div>
          <div class="skeleton mb-2" style="height:20px;width:85%;"></div>
          <div class="skeleton mb-4" style="height:14px;width:40%;"></div>
          <div class="skeleton" style="height:14px;width:70%;"></div>
          <div class="skeleton mt-2" style="height:14px;width:55%;"></div>
        </div>`;
      papersGrid.appendChild(col);
    }
  }

  function renderPapers(papers) {
    papersGrid.innerHTML = '';
    const start = (page - 1) * limit + 1;
    const end   = Math.min(page * limit, total);
    if (rangeText) rangeText.textContent = `${start.toLocaleString('id-ID')}–${end.toLocaleString('id-ID')}`;

    papers.forEach((p, i) => {
      const col = document.createElement('div');
      col.className = `col-md-6 col-lg-4 animate-fade-up delay-${Math.min(i % 6 + 1, 6)}`;
      const pid = p.paper_id || p.paperId || '';

      col.innerHTML = `
        <div class="magic-card h-100" style="display:flex;flex-direction:column;">
          <div style="padding:1.25rem 1.25rem 0.5rem; flex:1;">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <span class="badge-glass">${p.year || 'N/A'}</span>
              <a href="https://semanticscholar.org/paper/${pid}" target="_blank"
                 style="color:var(--text-3);transition:color 0.2s;" onmouseover="this.style.color='#818cf8'" onmouseout="this.style.color='var(--text-3)'"
                 title="Buka di Semantic Scholar">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5z"/>
                  <path d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0v-5z"/>
                </svg>
              </a>
            </div>
            <a href="/paper/${pid}" style="text-decoration:none;">
              <h5 class="fw-semibold text-gradient clamp-2 mb-2" style="font-size:0.95rem;line-height:1.45;">${p.title || '—'}</h5>
            </a>
            <p class="clamp-3 mb-0" style="color:var(--text-2);font-size:0.82rem;line-height:1.65;">${p.abstract || 'Tidak ada abstrak.'}</p>
          </div>
          <hr class="divider mx-0">
          <div style="padding:0.75rem 1.25rem 1rem;">
            <p class="mb-0 clamp-1" style="font-size:0.78rem;font-weight:500;color:var(--text-1);">${p.authors || 'Unknown Authors'}</p>
            <p class="mb-0 clamp-1" style="font-size:0.74rem;color:var(--text-3);">${p.venue || '—'}</p>
          </div>
        </div>`;
      papersGrid.appendChild(col);
    });
  }

  function renderPagination() {
    const maxPage = Math.ceil(total / limit);
    prevBtn.disabled = page <= 1;
    nextBtn.disabled = page >= maxPage;

    // Page dots
    if (pageDots) {
      pageDots.innerHTML = '';
      const range = [];
      for (let p2 = Math.max(1, page - 2); p2 <= Math.min(maxPage, page + 2); p2++) range.push(p2);
      range.forEach(p2 => {
        const btn = document.createElement('button');
        btn.className = `page-btn${p2 === page ? ' active' : ''}`;
        btn.textContent = p2;
        btn.addEventListener('click', () => { page = p2; fetchData(); });
        pageDots.appendChild(btn);
      });
    }
  }

  // ── Shared Toast ─────────────────────────────────────────
  window.toast = function (msg, ms = 3000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const el = document.createElement('div');
    el.className = 'toast-item';
    el.textContent = msg;
    container.appendChild(el);
    setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity 0.3s'; setTimeout(() => el.remove(), 350); }, ms);
  };

})();
