# Spesifikasi Alat Deteksi Plagiarisme Web-based untuk Mahasiswa

## 1. Ringkasan Proyek
Alat web sederhana yang memungkinkan mahasiswa mengunggah dokumen PDF untuk diperiksa keasliannya terhadap sumber akademik online (seperti Semantic Scholar, Sinta, Garuda, dan sumber akademik lainnya). Output berupa laporan kemiripan dengan persentase, daftar sumber yang cocok, dan highlight teks yang overlap. Alat ini ditujukan untuk penggunaan individu mahasiswa sebelum mengumpulkan tugas.

## 2. Pengguna Target
- Mahasiswa (skala kecil: ~15 orang, 1 tugas per minggu)

## 3. Fitur Utama (MVP)
- Unggah file PDF (hanya PDF untuk MVP)
- Ekstraksi teks dari PDF
- Preprocessing teks: penghapusan header/footer, nomor halaman, dan opsi untuk mengecualikan bagian kutipan/bibliografi
- Pembagian teks menjadi chunks (kalimat atau paragraf)
- Pencarian sumber akademik terkait via API publik:
  - Semantic Scholar API (free)
  - Sinta API (jika tersedia)
  - Garuda API (jika tersedia)
  - Alternatif: Google Custom Search API (free tier terbatas) untuk pencarian web akademik
- Pengambilan teks sumber (abstrak atau full text jika tersedia) dari hasil pencarian
- Perhitungan similarity menggunakan TF-IDF dan cosine similarity antara tiap chunk dan teks sumber
- Penyamaan skor similarity per chunk dan aggregasi menjadi skor keseluruhan (misalnya: rata-rata tertinggi atau max)
- Laporan:
  - Persentase kemiripan keseluruhan
  - Daftar sumber yang cocok dengan skor similarity dan judul
  - Tampilan teks asli dengan highlight pada bagian yang terdeteksi overlap (opsional: hasil sebagai HTML atau PDF yangдиhighlight)
  - Opsi untuk mengecualikan kutipan/bibliografi (checkbox)
- Tampilan hasil yang ramah pengguna (upload form, area hasil, tombol unduh laporan jika diperlukan)

## 4. Non-Fungsional
- Responsivitas: dasar desktop (mobile optional)
- Keamanan: file PDF dihapus setelah proses selesai (tidak disimpan permanen)
- Performa: untuk 15 pengguna, jeda beberapa detik hingga puluhan detik per upload tergantung pada latensi API
- Skalabilitas: arsitektur sederhana yang dapat di-scale dengan menambahkan instance jika diperlukan (misalnya menggunakan gunicorn + workers)
- Teknis: dapat dijalankan pada lingkungan lokal atau deploy ke layanan cloud gratis (Render, Railway, Fly.io) dengan batasan kuota API yang dipertimbangkan.

## 5. Arsitektur dan Alur Data
```
[Browser] --(Upload PDF)--> [Frontend (HTML/JS)] 
                                   |
                                   v
                        [Backend (Flask/FastAPI)]
                                   |
          +----------------------+----------------------+
          |                      |                      |
          v                      v                      v
[PDF Text Extraction]   [Preprocessing]        [Chunking]
          |                      |                      |
          +----------+-----------+----------+-----------+
                     |                          |
                     v                          v
          [Query Academic APIs]    [Optional: Exclude Ref Section]
                     |                          |
                     v                          v
          [Fetch Source Texts] <----------------+
                     |                          |
                     +----------+---------------+
                                |
                                v
                     [Similarity Computation (TF-IDF + Cosine)]
                                |
                                v
                     [Aggregate Similarity Scores]
                                |
                                v
                     [Generate Report]
                                |
                                v
                     [Return Result to Frontend]
```

## 6. Teknologi yang Direkomendasikan
- **Backend**: Python 3.9+, Flask atau FastAPI
- **Ekstraksi PDF**: PyMuPDF (fitz) atau pdfminer.six
- **Preprocessing & NLP**: NLTK (sentence tokenisasi), regex untuk deteksi bagian referensi, sklearn.feature_extraction.text.TfidfVectorizer, sklearn.metrics.pairwise.cosine_similarity
- **HTTP Client**: requests
- **Frontend**: HTML5, CSS3 (Bootstrap 5 untuk tampilan yang rapi), Vanilla JS atau minimal React (opsional)
- **Deploy**: Docker opsional; bisa langsung dijalankan dengan gunicorn atau uvicorn di layanan seperti Render (free tier), Railway, atau Fly.io

## 7. Algoritma Deteksi Plagiarisme (Rincian)
1. Ekstraksi teks mentah dari PDF.
2. Deteksi dan hapus bagian referensi/bibliografi jika opsi diaktifkan (menggunakan pola seperti "^Daftar Pustaka$", "^References$", "^Bibliografi$", serta pola penomoran referensi).
3. Tokenisasi teks menjadi kalimat menggunakan nltk.sent_tokenize.
4. Gabungkan kalimat menjadi chunks ukuran tetap (misalnya 3-5 kalimat) untuk meningkatkan konteks.
5. Untuk setiap chunk:
   a. Buat query pencarian ke Semantic Scholar API (atau sumber lain) dengan mengirimkan chunk sebagai query.
   b. Ambil hasil top-N (misal N=3) dan untuk setiap hasil, ambil judul dan abstrak (jika tersedia) atau coba buka URL untuk mengambil teks full text jika diizinkan dan tidak terlalu besar.
   c. Gabungkan judul + abstrak (atau full text) sebagai teks sumber.
   d. Hitung vektor TF-IDF untuk chunk dan teks sumber, lalu hitung cosine similarity.
   e. Similarkan skor similarity tertinggi untuk chunk tersebut.
6. Agregasi skor similarity seluruh chunk: gunakan rata-rata skor tertinggi per chunk, atau persentase chunk yang memiliki similarity > ambang (misal 0.7).
7. Persentase kemiripan akhir = (agregasi skor) * 100, dibatasi maksimal 100%.
8. Untuk laporan sumber: kumpulkan sumber yang memberikan similarity tertinggi per chunk, hapus duplikat, sorting berdasarkan skor similarity turun-temurun, tampilkan top-5 atau semua.
9. Highlighting: tandai chunk dalam teks asli yang memiliki similarity > ambang (misal 0.5) dengan warna kuning atau merah dalam tampilan HTML.

## 8. Batasan dan Asumsi
- Mengingat skala kecil, ketergantungan pada API gratis seperti Semantic Scholar memiliki batasan rate limit; kita akan mengimplementasikan caching sederhana (membuat hash dari chunk dan menyimpan hasil pencarian selama beberapa jam) untuk mengurangi panggilan berulang.
- Jika API akademik tidak memberikan teks lengkap, kita hanya mengandalkan abstrak; ini mungkin mengurangi akurasi untuk deteksi plagiarisme parafrasa yang lebih panjang.
- Opsi pengecualian bibliografi mengandalkan heuristik dan mungkin tidak sempurna untuk semua gaya penulisan.
- Tidak ada jaminan deteksi plagiarisme dari sumber yang tidak terindeks oleh API akademik yang digunakan (misalnya blog, situs non-akademik). Namun, fokus adalah sumber akademik seperti yang diminta pengguna.
- Untuk skala yang lebih besar di masa depan, mungkin perlu beralih ke layanan komersial atau membangun indeks sendiri melalui crawling teratur.

## 9. Rencana Milestone (TODO List)
- [ ] Siapkan repositori proyek dan struktur folder
- [ ] Implementasi ekstraksi teks dari PDF (PyMuPDF)
- [ ] Implementasi preprocessing: hapus header/footer, nomor halaman
- [ ] Implementasi deteksi dan penghapusan bagian referensi/bibliografi (regex)
- [ ] Implementasi tokenisasi kalimat dan pembuatan chunk
- [ ] Integrasi dengan Semantic Scholar API: endpoint pencarian dan pengambilan abstrak
- [ ] Implementasi fungsi similarity (TF-IDF + cosine similarity)
- [ ] Implementasi agregasi skor dan pembentukan laporan JSON
- [ ] Buat frontend sederhana: form upload, tampilkan hasil
- [ ] Hubungkan frontend dengan backend via fetch/AJAX
- [ ] Tambah opsi checkbox untuk mengecualikan kutipan/bibliografi
- [ ] Implementasi highlighting teks hasil di frontend (menandai overlap)
- [ ] Uji coba dengan dokumen contoh (PDF dari sumber akademik dan plagiarisme buatan)
- [ ] Perbaiki error handling dan penanganan batasan API (rate limit, timeout)
- [ ] Tambah caching sederhana untuk hasil pencarian API (misal menggunakan flask-caching atau dictionary sederhana)
- [ ] Dokumentasi penggunaan (README.md)
- [ ] Deploy ke layanan gratis (Render/Railway) dan condividkan link uji coba

## 10. Catatan Tambahan
- Pengguna harus mengerti bahwa alat ini bukan pengganti Turnitin secara penuh, tetapi dapat membantu mendeteksi kecurangan berbasis sumber akademik yang terindeks.
- Untuk hasil yang lebih akurat, disarankan menggunakan teks yang sudah bersih (tanpa watermark, gambar sebagai teks) karena ekstraksi PDF dari gambar tidak dilakukan dalam MVP ini (hanya teks tertanam).
- Jika waktu dan sumber daya memungkinkan, pertimbangkan untuk menambahkan dukungan untuk file DOCX dan TXT pada iterasi selanjutnya.
