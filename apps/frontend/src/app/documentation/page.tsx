'use client';
import { useEffect } from 'react';

export default function DocumentationPage() {
  useEffect(() => {
    const pages = document.getElementsByClassName('book-page') as HTMLCollectionOf<HTMLElement>;
    for (let i = 0; i < pages.length; i++) {
      if (i % 2 === 0) {
        pages[i].style.zIndex = String(pages.length - i);
      }
    }

    const handlePageClick = function (this: HTMLElement) {
      const pageNum = parseInt(this.getAttribute('data-page-num') || '0');
      if (pageNum % 2 === 0) {
        this.classList.remove('flipped');
        const prev = this.previousElementSibling as HTMLElement | null;
        if (prev) prev.classList.remove('flipped');
      } else {
        this.classList.add('flipped');
        const next = this.nextElementSibling as HTMLElement | null;
        if (next) next.classList.add('flipped');
      }
    };

    for (let i = 0; i < pages.length; i++) {
      pages[i].setAttribute('data-page-num', String(i + 1));
      pages[i].addEventListener('click', handlePageClick);
    }

    return () => {
      for (let i = 0; i < pages.length; i++) {
        pages[i].removeEventListener('click', handlePageClick);
      }
    };
  }, []);

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap');

        .doc-wrapper {
          min-height: 100vh;
          background: linear-gradient(135deg, #0f0c29, #1a1a3e, #24243e);
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 3em 1em 4em;
          position: relative;
          overflow: hidden;
        }
        .doc-wrapper::before {
          content: '';
          position: fixed;
          inset: 0;
          background:
            radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.15) 0%, transparent 40%),
            radial-gradient(ellipse at 80% 20%, rgba(168,85,247,0.15) 0%, transparent 40%),
            radial-gradient(ellipse at 60% 80%, rgba(59,130,246,0.1) 0%, transparent 40%);
          pointer-events: none;
          z-index: 0;
        }
        .doc-header {
          position: relative;
          z-index: 10;
          text-align: center;
          margin-bottom: 2em;
        }
        .doc-header .badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: rgba(99,102,241,0.15);
          border: 1px solid rgba(99,102,241,0.4);
          border-radius: 100px;
          padding: 6px 16px;
          font-size: 0.75rem;
          letter-spacing: 0.15em;
          text-transform: uppercase;
          color: #a5b4fc;
          margin-bottom: 1em;
          backdrop-filter: blur(8px);
        }
        .doc-header .badge .dot {
          width: 6px; height: 6px;
          border-radius: 50%;
          background: #6366f1;
          animation: pulse-dot 2s ease-in-out infinite;
        }
        @keyframes pulse-dot {
          0%,100%{transform:scale(1);opacity:1;}
          50%{transform:scale(1.4);opacity:0.6;}
        }
        .doc-header h1 {
          font-family: 'Cinzel', serif;
          font-size: clamp(1.5rem, 4vw, 2.8rem);
          font-weight: 700;
          background: linear-gradient(135deg, #e0e7ff, #a5b4fc, #818cf8);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          margin: 0 0 0.3em 0;
          letter-spacing: 0.05em;
        }
        .doc-header p { color: #94a3b8; font-size: 0.9rem; margin: 0; }

        .hint-text {
          position: relative; z-index: 10;
          color: #64748b; font-size: 0.78rem;
          margin-bottom: 1.5em;
          display: flex; align-items: center; gap: 8px;
        }
        .hint-text svg { opacity: 0.6; animation: bounce-hint 2s ease-in-out infinite; }
        @keyframes bounce-hint {
          0%,100%{transform:translateX(0);}
          50%{transform:translateX(4px);}
        }

        .book-scene { perspective: 250vw; position: relative; z-index: 10; }
        .book-pages {
          width: 80vw;
          max-width: 1000px;
          height: 55vw;
          max-height: 688px;
          position: relative;
          transform-style: preserve-3d;
          backface-visibility: hidden;
          border-radius: 4px;
          filter: drop-shadow(0 40px 80px rgba(0,0,0,0.6));
        }
        .book-page {
          position: absolute;
          top: 0;
          width: 50%;
          height: 100%;
          transform-origin: 0 0;
          transition: transform 1.4s cubic-bezier(0.645,0.045,0.355,1.000);
          backface-visibility: hidden;
          transform-style: preserve-3d;
          cursor: pointer;
          user-select: none;
          background: #f5f0e8;
          overflow: hidden;
        }
        .book-page::before {
          content: '';
          position: absolute;
          top:0;bottom:0;left:0;right:0;
          transition: background 0.7s;
          z-index: 100;
          pointer-events: none;
        }
        .book-page:nth-child(odd) {
          pointer-events: all;
          transform: rotateY(0deg);
          right: 0;
          border-radius: 0 4px 4px 0;
          border-left: 1px solid rgba(0,0,0,0.1);
          box-shadow: inset -5px 0 20px rgba(0,0,0,0.08);
        }
        .book-page:nth-child(odd)::before { background: rgba(0,0,0,0); }
        .book-page:nth-child(odd):hover::before { background: rgba(0,0,0,0.03); }
        .book-page:nth-child(odd):hover { transform: rotateY(-15deg); }
        .book-page:nth-child(even) {
          pointer-events: none;
          transform: rotateY(180deg);
          transform-origin: 100% 0;
          left: 0;
          border-radius: 4px 0 0 4px;
          border-right: 1px solid rgba(0,0,0,0.1);
          box-shadow: inset 5px 0 20px rgba(0,0,0,0.08);
        }
        .book-page:nth-child(even)::before { background: rgba(0,0,0,0.18); }
        .book-page.flipped:nth-child(odd) { pointer-events: none; transform: rotateY(-180deg); }
        .book-page.flipped:nth-child(odd)::before { background: rgba(0,0,0,0.18); }
        .book-page.flipped:nth-child(even) { pointer-events: all; transform: rotateY(0deg); }
        .book-page.flipped:nth-child(even):hover { transform: rotateY(15deg); }
        .book-page.flipped:nth-child(even):hover::before { background: rgba(0,0,0,0.03); }
        .book-page.flipped:nth-child(even)::before { background: rgba(0,0,0,0); }

        /* Page content */
        .page-content {
          width: 100%; height: 100%;
          overflow: hidden;
          display: flex; flex-direction: column;
          background: linear-gradient(160deg, #faf8f3 0%, #f5f0e8 100%);
          font-family: 'EB Garamond', serif;
          position: relative;
        }
        .page-content::after {
          content: '';
          position: absolute;
          left:0;top:0;bottom:0;width:12px;
          background: linear-gradient(to right, rgba(0,0,0,0.08), transparent);
          pointer-events: none;
        }
        .book-page:nth-child(even) .page-content::after {
          left:auto;right:0;
          background: linear-gradient(to left, rgba(0,0,0,0.08), transparent);
        }

        .page-header {
          background: linear-gradient(135deg, #1a1a3e 0%, #2d2b69 100%);
          padding: 0.6em 1.2em;
          display: flex;
          align-items: center;
          gap: 8px;
          flex-shrink: 0;
        }
        .page-header .logo-mark {
          width: 22px;height:22px;
          background: linear-gradient(135deg, #6366f1, #a855f7);
          border-radius: 5px;
          display:flex;align-items:center;justify-content:center;
          font-size:9px;font-weight:700;color:white;
          font-family:'Cinzel',serif;
          flex-shrink:0;
        }
        .page-header-title {
          font-family:'Cinzel',serif;
          font-size:0.6em;color:#a5b4fc;
          letter-spacing:0.1em;text-transform:uppercase;
        }
        .page-body {
          padding: 0.8em 1.2em;
          flex:1;overflow:hidden;
          display:flex;flex-direction:column;
        }
        .page-main-title {
          font-family:'Cinzel',serif;
          font-size:clamp(0.75em,1.8vw,1.2em);
          font-weight:700;color:#1a1a3e;
          margin:0 0 0.35em 0;line-height:1.2;
        }
        .page-subtitle {
          font-size:clamp(0.5em,1.1vw,0.78em);
          color:#6366f1;font-weight:600;
          margin-bottom:0.4em;
          text-transform:uppercase;letter-spacing:0.08em;
        }
        .page-divider {
          height:2px;
          background:linear-gradient(to right,#6366f1,#a855f7,transparent);
          margin-bottom:0.7em;border-radius:2px;
        }
        .page-text {
          font-size:clamp(0.48em,1.05vw,0.78em);
          line-height:1.65;color:#2d3748;
          margin-bottom:0.5em;
        }
        .page-text p{margin:0 0 0.4em 0;}

        .highlight-box {
          background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(168,85,247,0.05));
          border:1px solid rgba(99,102,241,0.25);
          border-left:3px solid #6366f1;
          border-radius:6px;
          padding:0.5em 0.7em;
          margin-bottom:0.45em;
          font-size:clamp(0.45em,0.95vw,0.72em);
          color:#2d3748;line-height:1.55;
        }
        .highlight-box .hb-title {
          font-weight:700;color:#6366f1;
          font-family:'Cinzel',serif;
          margin-bottom:0.25em;
          font-size:0.88em;text-transform:uppercase;letter-spacing:0.05em;
        }
        .warning-box {
          background:linear-gradient(135deg,rgba(239,68,68,0.07),rgba(234,179,8,0.04));
          border:1px solid rgba(239,68,68,0.2);
          border-left:3px solid #ef4444;
          border-radius:6px;
          padding:0.5em 0.7em;
          margin-bottom:0.45em;
          font-size:clamp(0.45em,0.95vw,0.72em);
          color:#2d3748;line-height:1.55;
        }
        .warning-box .hb-title {
          font-weight:700;color:#dc2626;
          font-family:'Cinzel',serif;
          margin-bottom:0.25em;
          font-size:0.88em;text-transform:uppercase;letter-spacing:0.05em;
        }

        .feature-list {
          list-style:none;margin:0;padding:0;
          display:flex;flex-direction:column;gap:0.25em;
        }
        .feature-list li {
          display:flex;align-items:flex-start;gap:0.45em;
          font-size:clamp(0.45em,0.95vw,0.72em);
          color:#374151;line-height:1.4;
        }
        .feature-list li::before {
          content:'◆';color:#6366f1;font-size:0.55em;
          flex-shrink:0;margin-top:0.4em;
        }

        .zone-badges {
          display:flex;gap:0.4em;flex-wrap:wrap;margin:0.35em 0;
        }
        .zone-badge {
          padding:0.18em 0.55em;border-radius:100px;
          font-size:clamp(0.4em,0.8vw,0.62em);
          font-weight:600;letter-spacing:0.05em;
        }
        .zone-safe{background:rgba(34,197,94,0.15);color:#16a34a;border:1px solid rgba(34,197,94,0.3);}
        .zone-warn{background:rgba(234,179,8,0.15);color:#ca8a04;border:1px solid rgba(234,179,8,0.3);}
        .zone-danger{background:rgba(239,68,68,0.15);color:#dc2626;border:1px solid rgba(239,68,68,0.3);}

        .tech-stack{display:grid;grid-template-columns:repeat(2,1fr);gap:0.28em;margin-top:0.25em;}
        .tech-item {
          background:rgba(99,102,241,0.07);
          border:1px solid rgba(99,102,241,0.15);
          border-radius:5px;
          padding:0.28em 0.45em;
          font-size:clamp(0.4em,0.82vw,0.62em);
          color:#374151;
        }
        .tech-item strong{color:#6366f1;display:block;font-size:0.82em;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.08em;}

        .notif-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:0.3em;margin-top:0.3em;}
        .notif-item {
          background:rgba(99,102,241,0.07);
          border:1px solid rgba(99,102,241,0.15);
          border-radius:5px;
          padding:0.28em 0.45em;
          font-size:clamp(0.4em,0.82vw,0.62em);
          color:#374151;
          display:flex;align-items:center;gap:0.35em;
        }
        .notif-icon{font-size:0.9em;flex-shrink:0;}

        .url-table{width:100%;border-collapse:collapse;font-size:clamp(0.4em,0.82vw,0.62em);margin-top:0.3em;}
        .url-table th{
          background:rgba(99,102,241,0.12);color:#6366f1;
          font-family:'Cinzel',serif;font-size:0.85em;letter-spacing:0.06em;
          padding:0.35em 0.5em;text-align:left;
          border-bottom:1px solid rgba(99,102,241,0.2);
        }
        .url-table td{padding:0.3em 0.5em;color:#374151;border-bottom:1px solid rgba(0,0,0,0.06);}
        .url-table tr:last-child td{border-bottom:none;}
        .url-table code{background:rgba(99,102,241,0.1);border-radius:3px;padding:0.1em 0.3em;font-family:'Courier New',monospace;font-size:0.9em;color:#6366f1;}

        .roadmap-phase {
          background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(168,85,247,0.07));
          border:1px solid rgba(99,102,241,0.2);
          border-radius:8px;
          padding:0.5em 0.7em;
          margin-bottom:0.4em;
        }
        .roadmap-phase .phase-label{
          font-family:'Cinzel',serif;
          font-size:clamp(0.42em,0.85vw,0.65em);
          color:#a855f7;font-weight:600;
          text-transform:uppercase;letter-spacing:0.08em;
          margin-bottom:0.2em;
        }
        .roadmap-phase .phase-title{font-weight:700;color:#1a1a3e;font-size:clamp(0.48em,0.98vw,0.74em);margin-bottom:0.18em;}
        .roadmap-phase .phase-desc{font-size:clamp(0.42em,0.85vw,0.64em);color:#4b5563;line-height:1.45;}

        .page-footer {
          padding:0.45em 1.2em;
          border-top:1px solid rgba(99,102,241,0.15);
          display:flex;align-items:center;justify-content:space-between;
          flex-shrink:0;
        }
        .page-num{font-family:'Cinzel',serif;font-size:clamp(0.38em,0.75vw,0.55em);color:#94a3b8;letter-spacing:0.1em;}
        .page-watermark{font-family:'Cinzel',serif;font-size:clamp(0.36em,0.7vw,0.52em);color:#cbd5e1;letter-spacing:0.08em;}

        /* Cover page */
        .cover-page{background:linear-gradient(155deg,#0f0c29 0%,#1a1a3e 40%,#2d2b69 100%);}
        .cover-page .page-content{background:transparent;align-items:center;justify-content:center;text-align:center;position:relative;}
        .cover-page .page-content::after{display:none;}
        .cover-bg-circles{position:absolute;inset:0;overflow:hidden;}
        .cover-bg-circles::before{
          content:'';position:absolute;
          width:60%;height:60%;top:-10%;right:-15%;
          background:radial-gradient(circle,rgba(99,102,241,0.25) 0%,transparent 70%);
          border-radius:50%;
        }
        .cover-bg-circles::after{
          content:'';position:absolute;
          width:50%;height:50%;bottom:-10%;left:-10%;
          background:radial-gradient(circle,rgba(168,85,247,0.2) 0%,transparent 70%);
          border-radius:50%;
        }
        .cover-inner{position:relative;z-index:2;padding:1.5em;display:flex;flex-direction:column;align-items:center;}
        .cover-logo{
          width:100px;height:auto;
          display:flex;align-items:center;justify-content:center;
          margin-bottom:0.9em;
        }
        .cover-logo img {
          width:100%;height:auto;
          object-fit:contain;
          filter: drop-shadow(0 8px 16px rgba(0,0,0,0.3));
        }
        .cover-title{
          font-family:'Cinzel',serif;
          font-size:clamp(0.9em,2.3vw,1.6em);font-weight:700;
          background:linear-gradient(135deg,#e0e7ff,#a5b4fc);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
          line-height:1.2;margin-bottom:0.25em;
        }
        .cover-abbr{
          font-family:'Cinzel',serif;
          font-size:clamp(1.3em,3.2vw,2.4em);font-weight:700;
          background:linear-gradient(135deg,#818cf8,#c084fc);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
          letter-spacing:0.12em;margin-bottom:0.6em;
        }
        .cover-tagline{font-size:clamp(0.48em,1vw,0.75em);color:#94a3b8;max-width:80%;line-height:1.6;margin-bottom:1em;}
        .cover-divider{width:55px;height:2px;background:linear-gradient(to right,#6366f1,#a855f7);border-radius:2px;margin-bottom:1em;}
        .cover-meta{font-family:'Cinzel',serif;font-size:clamp(0.38em,0.75vw,0.56em);color:#475569;letter-spacing:0.15em;text-transform:uppercase;}

        /* Back cover - BLANK/POLOS */
        .back-cover-blank{background:linear-gradient(155deg,#2d2b69 0%,#1a1a3e 60%,#0f0c29 100%);}
        .back-cover-blank .page-content{background:transparent;}
        .back-cover-blank .page-content::after{display:none;}

        /* Page indicator dots */
        .page-indicators{
          position:relative;z-index:10;
          display:flex;gap:6px;margin-top:1.5em;
          align-items:center;justify-content:center;
        }
        .pi-spread{
          width:6px;height:6px;border-radius:50%;
          background:rgba(99,102,241,0.3);
          transition:all 0.3s;
        }
        .pi-spread.active{
          background:#6366f1;
          transform:scale(1.3);
        }
      `}</style>

      <div className="doc-wrapper">
        <div className="doc-header">
          <div className="badge">
            <span className="dot"></span>
            Dokumentasi AIMS
          </div>
          <h1>AIMS Documentation</h1>
          <p>Academic Intelligence Management System · Panduan Sistem &amp; Pengembangan</p>
        </div>

        <div className="hint-text">
          <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
          </svg>
          Klik halaman untuk membalik
        </div>

        <div className="book-scene">
          <div className="book-pages">

            {/* ── PAGE 1 (odd) ── Cover Depan */}
            <div className="book-page cover-page">
              <div className="page-content">
                <div className="cover-bg-circles"></div>
                <div className="cover-inner">
                  <div className="cover-logo"><img src="/unhas-logo.jpg" alt="Universitas Hasanuddin Logo" /></div>
                  <div className="cover-title">Academic Intelligence<br />Management System</div>
                  <div className="cover-abbr">AIMS</div>
                  <div className="cover-divider"></div>
                  <div className="cover-tagline">
                    Platform Pendamping NeoSIA untuk Monitoring Akademik, Artificial Intelligence, dan Otomatisasi Layanan Akademik
                  </div>
                  <div className="cover-meta">Fakultas Ilmu Budaya · Universitas Hasanuddin</div>
                </div>
              </div>
            </div>

            {/* ── PAGE 2 (even) ── Pendahuluan 1 */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Pendahuluan</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Pendahuluan</div>
                  <div className="page-divider"></div>
                  <div className="page-text">
                    <p><strong>Academic Intelligence Management System (AIMS)</strong> merupakan platform manajemen informasi akademik yang dirancang untuk mendukung pengelolaan data akademik, pemantauan perkembangan studi mahasiswa, serta pelaksanaan <em>Academic Early Warning System</em> sebagai bagian dari upaya peningkatan kualitas layanan akademik di perguruan tinggi.</p>
                    <p>Berbeda dengan sistem informasi akademik konvensional yang umumnya berfungsi sebagai media pencatatan dan penyajian data, AIMS dikembangkan untuk mendukung proses pemantauan akademik secara aktif.</p>
                    <p>Sistem tidak hanya menyimpan informasi akademik mahasiswa, tetapi juga melakukan evaluasi berkala terhadap perkembangan studi sehingga potensi permasalahan akademik dapat dideteksi lebih dini.</p>
                  </div>
                  <div className="highlight-box" style={{marginTop: '0.4em'}}>
                    <div className="hb-title">Pemantauan Otomatis</div>
                    Melalui mekanisme pemantauan otomatis, sistem dapat mengidentifikasi mahasiswa yang mengalami penurunan prestasi akademik atau berpotensi mengalami keterlambatan penyelesaian studi. Hasil evaluasi tersebut kemudian digunakan sebagai dasar penyampaian notifikasi kepada mahasiswa serta informasi kepada Dosen Penasehat Akademik (PA), sehingga proses pembimbingan dapat dilakukan secara lebih cepat, tepat sasaran, dan terdokumentasi.
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">02</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 3 (odd) ── Pendahuluan 2 */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Pendahuluan</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Ekspansi Learning Feed</div>
                  <div className="page-divider"></div>
                  <div className="page-text">
                    <p>Selain mendukung fungsi pemantauan akademik, AIMS dirancang untuk berkembang menjadi platform yang mengintegrasikan aktivitas pembelajaran melalui konsep <strong>Learning Feed</strong> berbasis mata kuliah.</p>
                    <p>Setiap mata kuliah memiliki ruang pembelajaran digital (Learning Feed) yang secara otomatis terbentuk berdasarkan data akademik pada sistem induk. Dosen pengampu berperan sebagai host, sedangkan mahasiswa yang terdaftar melalui Kartu Rencana Studi (KRS) menjadi peserta pada Learning Feed tersebut.</p>
                  </div>
                  <div className="page-subtitle">Aktivitas Terpusat</div>
                  <ul className="feature-list" style={{marginBottom: '0.5em'}}>
                    <li>Learning Feed berfungsi sebagai pusat aktivitas pembelajaran yang mengintegrasikan pengumuman, distribusi materi, diskusi akademik, pemberian tugas, pengumpulan tugas, serta umpan balik dari dosen dalam satu lingkungan yang terstruktur.</li>
                    <li>Mahasiswa hanya dapat mengakses Learning Feed sesuai dengan mata kuliah yang diambil, dan dosen hanya mengelola Learning Feed dari mata kuliah yang diampunya.</li>
                  </ul>
                  <div className="page-text" style={{fontStyle: 'italic', fontSize: '0.7em', color: '#6b7280'}}>
                    Seluruh keanggotaan dan hak akses dikelola secara otomatis melalui sinkronisasi dengan sistem akademik, sehingga tidak diperlukan proses pembuatan kelas atau pendaftaran peserta secara manual.
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">03</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 4 (even) ── Arsitektur Sistem */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Arsitektur Sistem</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Arsitektur Sistem</div>
                  <div className="page-divider"></div>
                  <div className="page-text">
                    <p>AIMS dibangun menggunakan arsitektur modular yang memisahkan layanan berdasarkan fungsi masing-masing sehingga sistem lebih mudah dikembangkan, dipelihara, dan diintegrasikan dengan sistem lain di lingkungan universitas.</p>
                  </div>
                  <div className="tech-stack" style={{gridTemplateColumns: '1fr', gap: '0.4em'}}>
                    <div className="tech-item">
                      <strong>Back-End</strong>
                      Bertugas mengelola data akademik, autentikasi pengguna, dan integrasi dengan sistem eksternal.
                    </div>
                    <div className="tech-item">
                      <strong>Dashboard Administrator</strong>
                      Digunakan untuk melakukan pemantauan kondisi akademik secara menyeluruh.
                    </div>
                    <div className="tech-item">
                      <strong>Portal Pengguna</strong>
                      Menyediakan antarmuka bagi mahasiswa, dosen, dosen pembimbing akademik, dan administrator.
                    </div>
                    <div className="tech-item">
                      <strong>Academic Agent</strong>
                      Modul otomatis yang melakukan evaluasi berkala terhadap data akademik berdasarkan aturan akademik.
                    </div>
                    <div className="tech-item">
                      <strong>Notification Service</strong>
                      Layanan yang mengirimkan informasi dan pengingat kepada mahasiswa maupun dosen.
                    </div>
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">04</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 5 (odd) ── Fitur Utama (Admin) */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Fitur Utama</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Fitur Utama Sistem</div>
                  <div className="page-divider"></div>
                  
                  <div className="page-subtitle">1. Dashboard Administrator</div>
                  <div className="page-text">
                    <p>Dashboard Administrator merupakan pusat kendali sistem yang digunakan oleh pengelola akademik untuk memantau kondisi akademik mahasiswa secara menyeluruh.</p>
                  </div>
                  <ul className="feature-list">
                    <li>Pengelolaan data mahasiswa.</li>
                    <li>Visualisasi statistik akademik berdasarkan program studi maupun angkatan.</li>
                    <li>Identifikasi mahasiswa berdasarkan tingkat risiko akademik.</li>
                    <li>Pengaturan parameter evaluasi akademik, seperti batas minimal IPK atau indikator risiko lainnya.</li>
                    <li>Pengelolaan konfigurasi sistem notifikasi.</li>
                    <li>Informasi perkuliahan & Absensi.</li>
                  </ul>
                  <div className="highlight-box" style={{marginTop: '0.6em'}}>
                    Dashboard ini memberikan gambaran kondisi akademik secara real-time sehingga dapat mendukung proses pengambilan keputusan di tingkat fakultas.
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">05</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 6 (even) ── Fitur Utama (PA & Mhs) */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Fitur Utama</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Fitur Utama Lanjutan</div>
                  <div className="page-divider"></div>

                  <div className="page-subtitle">2. Dashboard Dosen Penasehat Akademik (PA)</div>
                  <div className="page-text"><p>Dirancang untuk membantu dosen memantau perkembangan akademik mahasiswa bimbingannya.</p></div>
                  <ul className="feature-list" style={{marginBottom: '0.6em'}}>
                    <li>Daftar mahasiswa bimbingan.</li>
                    <li>Ringkasan perkembangan IPK, IPS, dan jumlah SKS.</li>
                    <li>Identifikasi mahasiswa yang memerlukan perhatian khusus.</li>
                    <li>Riwayat notifikasi akademik & Pencatatan hasil konsultasi.</li>
                  </ul>
                  
                  <div className="page-subtitle">3. Portal Mahasiswa</div>
                  <div className="page-text"><p>Menyediakan akses informasi akademik secara personal dan transparan.</p></div>
                  <ul className="feature-list">
                    <li>Profil akademik & Riwayat nilai setiap semester.</li>
                    <li>Grafik perkembangan IPS, IPK, dan jumlah SKS.</li>
                    <li>Estimasi pencapaian target kelulusan.</li>
                    <li>Pusat notifikasi akademik & Simulasi penyusunan KRS.</li>
                    <li>Akses menuju Learning Feed mata kuliah.</li>
                  </ul>
                </div>
                <div className="page-footer">
                  <span className="page-num">06</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 7 (odd) ── Learning Feed */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Learning Feed</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Learning Feed</div>
                  <div className="page-divider"></div>
                  <div className="page-subtitle" style={{textTransform: 'none', color: '#6366f1'}}>(Rencana Pengembangan Pendamping SIKOLA)</div>
                  <div className="page-text">
                    <p>Learning Feed merupakan ruang pembelajaran digital yang dirancang dengan pendekatan <em>feed-based interface</em>, yaitu antarmuka yang menyerupai pola interaksi media sosial yang telah akrab bagi sebagian besar pengguna.</p>
                    <p>Pendekatan ini dipilih untuk mengurangi kurva pembelajaran (learning curve), sehingga dosen maupun mahasiswa dapat beradaptasi dengan cepat tanpa memerlukan pelatihan yang kompleks.</p>
                  </div>
                  
                  <div className="page-subtitle">Aktivitas Kolaboratif</div>
                  <div className="tech-stack" style={{gap: '0.3em'}}>
                    <div className="tech-item" style={{padding: '0.4em'}}>
                      <strong>Melalui Learning Feed, dosen dapat:</strong>
                      <ul style={{margin:0, paddingLeft: '1.2em'}}>
                        <li>Membagikan materi</li>
                        <li>Memberikan pengumuman</li>
                        <li>Memberikan tugas</li>
                        <li>Membuka diskusi</li>
                      </ul>
                    </div>
                    <div className="tech-item" style={{padding: '0.4em'}}>
                      <strong>Mahasiswa dapat:</strong>
                      <ul style={{margin:0, paddingLeft: '1.2em'}}>
                        <li>Mengumpulkan tugas</li>
                        <li>Berdiskusi</li>
                        <li>Memberikan komentar</li>
                        <li>Memperoleh umpan balik</li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">07</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 8 (even) ── Academic Agent */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Academic Agent</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Academic Agent</div>
                  <div className="page-divider"></div>
                  
                  <div className="highlight-box" style={{marginBottom: '0.8em'}}>
                    <div className="hb-title">Agentic AI</div>
                    AIMS Menggunakan <strong>OPENCLAW</strong> sebagai AI Assistent. Academic Agent merupakan komponen utama yang membedakan AIMS dengan sistem informasi akademik konvensional.
                  </div>

                  <div className="page-subtitle">Modul Berjalan Otomatis Untuk:</div>
                  <ul className="feature-list">
                    <li>Melakukan evaluasi berkala terhadap data akademik mahasiswa.</li>
                    <li>Mengidentifikasi mahasiswa yang mengalami penurunan prestasi akademik.</li>
                    <li>Mendeteksi mahasiswa yang berpotensi mengalami keterlambatan studi.</li>
                    <li>Menghasilkan peringatan dini berdasarkan aturan akademik yang telah ditentukan.</li>
                    <li>Mengirimkan notifikasi kepada mahasiswa maupun Dosen Penasehat Akademik.</li>
                    <li>Memantau Aktivitas Learning Feed dan memberikan dokumentasi yang dibutuhkan pada tiap interaksi perkuliahan.</li>
                  </ul>
                  
                  <div className="page-text" style={{marginTop: '0.8em', fontSize: '0.7em', color: '#4b5563'}}>
                    Pada tahap pengembangan saat ini, Academic Agent menggunakan mekanisme <em>Rule Engine</em>, yaitu serangkaian aturan akademik yang dapat disesuaikan dengan kebijakan masing-masing institusi.
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">08</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 9 (odd) ── Notifikasi & Penutup */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Notifikasi & Penutup</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Sistem Notifikasi</div>
                  <div className="page-divider"></div>
                  <div className="page-text">
                    <p>AIMS menyediakan layanan notifikasi otomatis yang dapat diintegrasikan dengan berbagai media komunikasi, seperti WhatsApp, Telegram, maupun surat elektronik (email).</p>
                  </div>
                  <div className="notif-grid" style={{marginBottom: '0.8em'}}>
                    <div className="notif-item"><span className="notif-icon">📑</span>Pengingat KRS</div>
                    <div className="notif-item"><span className="notif-icon">📉</span>Penurunan IPK</div>
                    <div className="notif-item"><span className="notif-icon">⚠️</span>Risiko akademik</div>
                    <div className="notif-item"><span className="notif-icon">📅</span>Jadwal konsultasi</div>
                    <div className="notif-item"><span className="notif-icon">⏳</span>Batas masa studi</div>
                    <div className="notif-item"><span className="notif-icon">📢</span>Pengumuman akademik</div>
                  </div>

                  <div className="page-main-title">Penutup</div>
                  <div className="page-divider"></div>
                  <div className="page-text">
                    <p>Academic Intelligence Management System (AIMS) merupakan langkah strategis menuju tata kelola akademik yang lebih modern, terintegrasi, dan berbasis kecerdasan buatan.</p>
                  </div>
                  <div className="roadmap-phase" style={{marginTop: '0.4em'}}>
                    <div className="phase-desc" style={{fontStyle: 'italic', fontWeight: 'bold', color: '#1a1a3e'}}>
                      Implementasi AIMS di Fakultas Ilmu Budaya Universitas Hasanuddin diharapkan menjadi fondasi bagi pengembangan ekosistem Smart Campus yang adaptif terhadap perkembangan teknologi dan kebutuhan pendidikan tinggi di masa depan.
                    </div>
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">09</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 10 (even) ── Back Cover POLOS/BLANK */}
            <div className="book-page back-cover-blank">
              <div className="page-content">
              </div>
            </div>

          </div>
        </div>
      </div>
    </>
  );
}
