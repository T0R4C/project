/* Scholar AI — main.js */

(function () {
  'use strict';

  // ── Elements ──────────────────────────────────────────────
  const form        = document.getElementById('searchForm');
  const queryText   = document.getElementById('queryText');
  const submitBtn   = document.getElementById('submitBtn');
  const yearFrom    = document.getElementById('yearFrom');
  const yearTo      = document.getElementById('yearTo');
  const loadingState = document.getElementById('loadingState');
  const loadingDetail = document.getElementById('loadingDetail');
  const errorBox    = document.getElementById('errorBox');
  const errorMsg    = document.getElementById('errorMsg');
  const resultsSection = document.getElementById('resultsSection');
  const resultGrid  = document.getElementById('resultGrid');
  const resultsCount = document.getElementById('resultsCount');
  const poolInfo    = document.getElementById('poolInfo');

  // Keep results for export
  let lastResults = [];

  // ── Year Dropdowns ────────────────────────────────────────
  const currentYear = new Date().getFullYear();
  for (let y = currentYear; y >= 1990; y--) {
    yearFrom.add(new Option(y, y));
    yearTo.add(new Option(y, y));
  }
  yearTo.value = currentYear;

  // ── Load Stats ────────────────────────────────────────────
  async function loadStats() {
    try {
      const res  = await fetch('/api/stats');
      const data = await res.json();
      if (data.success) {
        animateCounter('statTotal', data.total_papers);
        document.getElementById('statLatest').textContent = data.latest_year || '—';
      }
    } catch (_) {}
  }

  function animateCounter(id, target) {
    const el = document.getElementById(id);
    if (!el || !target) return;
    let current = 0;
    const duration = 1200;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      current = Math.min(current + step, target);
      el.textContent = Math.floor(current).toLocaleString('id-ID');
      if (current >= target) clearInterval(timer);
    }, 16);
  }

  loadStats();

  // ── Topic Chips ───────────────────────────────────────────
  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      // Remove active from all
      document.querySelectorAll('.chip-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      queryText.value = btn.dataset.q;
      queryText.focus();
      toast('💡 Topik diterapkan. Klik "Cari" untuk menelusuri.', 2500);
    });
  });

  // ── Form Submit ───────────────────────────────────────────
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = queryText.value.trim();
      if (!text || text.length < 5) {
        toast('⚠️ Mohon masukkan kata kunci atau abstrak yang lebih panjang.', 3000);
        return;
      }
      await runSearch(text);
    });
  }

  async function runSearch(text) {
    // UI reset
    errorBox.classList.add('d-none');
    resultsSection.classList.add('d-none');
    resultGrid.innerHTML = '';
    loadingState.classList.remove('d-none');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>Menganalisis...`;

    const yf = yearFrom.value ? parseInt(yearFrom.value) : null;
    const yt = yearTo.value   ? parseInt(yearTo.value)   : null;

    const loadingMessages = [
      'Membangun indeks BM25…',
      'Mencocokkan n-gram frasa…',
      'Meranking berdasarkan relevansi…',
      'Hampir selesai…'
    ];
    let msgIdx = 0;
    const msgTimer = setInterval(() => {
      if (loadingDetail && msgIdx < loadingMessages.length) {
        loadingDetail.textContent = loadingMessages[msgIdx++];
      }
    }, 1500);

    try {
      const res  = await fetch('/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, year_from: yf, year_to: yt })
      });
      const data = await res.json();

      if (!res.ok || !data.success) throw new Error(data.error || 'Server error.');

      lastResults = data.results || [];
      renderResults(lastResults, data.pool_size, data.cached);

    } catch (err) {
      errorMsg.textContent = err.message;
      errorBox.classList.remove('d-none');
    } finally {
      clearInterval(msgTimer);
      loadingState.classList.add('d-none');
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16" class="me-2"><path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.118-.101zm-5.242.856a5.5 5.5 0 1 1 0-11 5.5 5.5 0 0 1 0 11z"/></svg>Cari Artikel Relevan`;
    }
  }

  // ── Render Results ────────────────────────────────────────
  function renderResults(papers, poolSize, cached) {
    resultGrid.innerHTML = '';
    resultsCount.textContent = `${papers.length} Artikel`;
    poolInfo.textContent = `Dianalisis dari ${(poolSize || 0).toLocaleString('id-ID')} jurnal${cached ? ' · ⚡ Dari cache' : ''}`;

    if (papers.length === 0) {
      resultGrid.innerHTML = `
        <div class="col-12">
          <div class="magic-card empty-state">
            <span class="empty-icon">🔍</span>
            <h5>Tidak Ada Kecocokan Relevan</h5>
            <p>Tidak ada artikel yang melampaui ambang relevansi. Coba gunakan istilah yang lebih umum, atau perluas rentang tahun.</p>
          </div>
        </div>`;
      resultsSection.classList.remove('d-none');
      return;
    }

    papers.forEach((paper, idx) => {
      const delay = `delay-${Math.min(idx + 1, 6)}`;
      const score = paper.relevance_score || 0;
      let badgeClass = 'badge-glass';
      if (score >= 60) badgeClass = 'badge-emerald';
      else if (score >= 35) badgeClass = 'badge-indigo';
      else if (score >= 20) badgeClass = 'badge-amber';

      // SVG ring
      const r = 19, circ = 2 * Math.PI * r;
      const offset = circ - (score / 100) * circ;
      const ringColor = score >= 60 ? '#10b981' : score >= 35 ? '#818cf8' : '#f59e0b';

      const col = document.createElement('div');
      col.className = `col-md-6 animate-fade-up ${delay}`;
      col.innerHTML = `
        <div class="magic-card h-100" style="display:flex;flex-direction:column;">
          <div style="padding:1.5rem 1.5rem 0.75rem;">
            <!-- Top Row -->
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="d-flex align-items-center gap-2 flex-wrap">
                <span class="badge-glass">${paper.year || 'N/A'}</span>
                <span class="${badgeClass}">${score}% cocok</span>
              </div>
              <!-- Relevance Ring -->
              <div class="relevance-ring" title="${score}% Relevansi">
                <svg width="48" height="48" viewBox="0 0 48 48">
                  <circle class="ring-bg" cx="24" cy="24" r="${r}" stroke-width="4"/>
                  <circle class="ring-fill" cx="24" cy="24" r="${r}" stroke-width="4"
                    stroke="${ringColor}"
                    stroke-dasharray="${circ}"
                    stroke-dashoffset="${offset}"/>
                </svg>
                <span style="font-size:0.6rem;font-weight:700;color:${ringColor};">${score}%</span>
              </div>
            </div>

            <!-- Title -->
            <a href="/paper/${paper.paperId}" class="d-block mb-2" style="text-decoration:none;">
              <h5 class="fw-bold text-gradient clamp-2 mb-0" style="font-size:1rem;line-height:1.45;">${paper.title}</h5>
            </a>

            <!-- Abstract -->
            <p class="clamp-3 mb-3" style="color:var(--text-2);font-size:0.85rem;line-height:1.65;">${paper.abstract || 'Tidak ada abstrak.'}</p>
          </div>

          <!-- Divider -->
          <hr class="divider mx-0">

          <!-- Footer -->
          <div style="padding:0.75rem 1.5rem 1.25rem;" class="mt-auto">
            <div class="d-flex align-items-center justify-content-between gap-2">
              <div class="overflow-hidden">
                <p class="mb-0 clamp-2" style="font-size:0.8rem;font-weight:500;color:var(--text-1);">${paper.authors || 'Unknown Authors'}</p>
                <p class="mb-0 clamp-1" style="font-size:0.75rem;color:var(--text-3);">${paper.venue || '—'}</p>
              </div>
              <div class="d-flex gap-2 flex-shrink-0">
                <button onclick="copyCitation(${JSON.stringify(paper).replace(/'/g,"&#39;")})" class="btn-glass py-1 px-2" style="font-size:0.75rem;" title="Salin Sitasi APA">
                  📋
                </button>
                <a href="/paper/${paper.paperId}" class="btn-glass py-1 px-2" style="font-size:0.75rem;" title="Lihat Detail">
                  Detail
                </a>
              </div>
            </div>
          </div>
        </div>`;
      resultGrid.appendChild(col);
    });

    resultsSection.classList.remove('d-none');
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // ── Copy Citation ─────────────────────────────────────────
  window.copyCitation = function (paper) {
    const authors = paper.authors || 'Unknown Authors';
    const year    = paper.year || 'n.d.';
    const title   = paper.title || 'Untitled';
    const venue   = paper.venue || '';
    const apa     = `${authors} (${year}). ${title}. ${venue}.`.trim();
    navigator.clipboard.writeText(apa).then(() => {
      toast(`📋 Sitasi disalin: ${apa.substring(0, 60)}…`, 3500);
    }).catch(() => toast('⚠️ Gagal menyalin sitasi.', 2500));
  };

  // ── Export CSV ────────────────────────────────────────────
  window.exportResults = function () {
    if (!lastResults.length) { toast('⚠️ Tidak ada hasil untuk diekspor.', 2500); return; }
    const header = ['Rank', 'Relevansi (%)', 'Judul', 'Penulis', 'Tahun', 'Venue', 'Paper ID'];
    const rows = lastResults.map((p, i) => [
      i + 1,
      p.relevance_score,
      `"${(p.title || '').replace(/"/g, '""')}"`,
      `"${(p.authors || '').replace(/"/g, '""')}"`,
      p.year || '',
      `"${(p.venue || '').replace(/"/g, '""')}"`,
      p.paperId || ''
    ]);
    const csv = [header, ...rows].map(r => r.join(',')).join('\n');
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = `scholar_ai_results_${Date.now()}.csv`;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast('✅ File CSV berhasil diunduh.', 2500);
  };

  // ── Toast ─────────────────────────────────────────────────
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
