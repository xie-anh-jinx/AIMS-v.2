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
                    Platform pendukung sistem informasi akademik untuk pemantauan proaktif perkembangan mahasiswa
                  </div>
                  <div className="cover-meta">Dokumentasi Sistem · Versi 1.0</div>
                </div>
              </div>
            </div>

            {/* ── PAGE 2 (even) ── Deskripsi AIMS */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Deskripsi</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Deskripsi</div>
                  <div className="page-divider"></div>
                  <div className="page-text">
                    <p>Academic Intelligence Management System (AIMS) merupakan platform pendukung sistem informasi akademik yang dirancang untuk membantu pimpinan perguruan tinggi, pimpinan program studi, dan Dosen Penasehat Akademik (PA) dalam melakukan pemantauan perkembangan akademik mahasiswa secara proaktif.</p>
                    <p>AIMS berfungsi sebagai sistem monitoring, koordinasi, dan pemberian notifikasi akademik, sehingga proses pembinaan mahasiswa dapat dilakukan lebih cepat, terdokumentasi, dan terukur.</p>
                  </div>
                  <div className="page-subtitle">AIMS sebagai Decision Support System</div>
                  <ul className="feature-list">
                    <li>Monitoring perkembangan akademik mahasiswa</li>
                    <li>Dokumentasi koordinasi antara Program Studi, Dosen PA, dan mahasiswa</li>
                    <li>Sistem notifikasi dan pengingat akademik</li>
                    <li>Dashboard analitik sebagai dasar pengambilan keputusan</li>
                  </ul>
                </div>
                <div className="page-footer">
                  <span className="page-num">01</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 3 (odd) ── Kebijakan Data */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Kebijakan Data</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Kebijakan Integritas &amp; Kedaulatan Data</div>
                  <div className="page-divider"></div>
                  <div className="warning-box">
                    <div className="hb-title">⚠ Penting</div>
                    Seluruh data akademik berasal dari <strong>Data Warehouse</strong> universitas melalui sinkronisasi <strong>satu arah (read-only)</strong> dari sistem akademik induk <strong>NeoSIA</strong>.
                  </div>
                  <div className="page-subtitle">AIMS Tidak Berwenang Untuk</div>
                  <ul className="feature-list" style={{marginBottom:'0.55em'}}>
                    <li>Menambah data akademik</li>
                    <li>Mengubah data akademik</li>
                    <li>Menghapus data akademik</li>
                    <li>Memanipulasi data pada NeoSIA</li>
                  </ul>
                  <div className="page-text" style={{fontStyle:'italic',fontSize:'clamp(0.44em,0.9vw,0.68em)',color:'#6b7280'}}>
                    Seluruh perubahan data akademik tetap dilakukan melalui sistem NeoSIA sesuai kewenangan yang berlaku.
                  </div>
                  <div className="page-subtitle">AIMS Menyediakan</div>
                  <ul className="feature-list">
                    <li>Monitoring perkembangan akademik mahasiswa</li>
                    <li>Dokumentasi koordinasi Program Studi, Dosen PA, dan mahasiswa</li>
                    <li>Sistem notifikasi dan pengingat akademik</li>
                    <li>Dashboard analitik pengambilan keputusan</li>
                  </ul>
                </div>
                <div className="page-footer">
                  <span className="page-num">02</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 4 (even) ── Tujuan & Keunggulan */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Tujuan &amp; Keunggulan</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Tujuan &amp; Keunggulan</div>
                  <div className="page-divider"></div>
                  <div className="page-text">
                    <p>AIMS dikembangkan untuk meningkatkan efektivitas pembinaan akademik melalui mekanisme <strong>early warning system</strong>.</p>
                  </div>

                  <div className="page-subtitle">Deteksi Dini Mahasiswa Berisiko</div>
                  <div className="page-text"><p>Klasifikasi tingkat risiko akademik mahasiswa secara otomatis berdasarkan indikator yang telah ditetapkan:</p></div>
                  <div className="zone-badges">
                    <span className="zone-badge zone-safe">🟢 Zona Aman</span>
                    <span className="zone-badge zone-warn">🟡 Zona Perhatian</span>
                    <span className="zone-badge zone-danger">🔴 Zona Risiko Tinggi</span>
                  </div>

                  <div className="page-subtitle" style={{marginTop:'0.5em'}}>Monitoring Proses Konseling</div>
                  <div className="page-text"><p>Seluruh komunikasi dan tindak lanjut antara pimpinan, Dosen PA, dan mahasiswa terdokumentasi sebagai <strong>log aktivitas</strong> yang dapat dipantau secara transparan.</p></div>

                  <div className="page-subtitle">Otomatisasi Notifikasi</div>
                  <div className="notif-grid">
                    <div className="notif-item"><span className="notif-icon">📋</span>Belum isi KRS</div>
                    <div className="notif-item"><span className="notif-icon">💳</span>Belum registrasi</div>
                    <div className="notif-item"><span className="notif-icon">📉</span>IPK/IPS di bawah batas</div>
                    <div className="notif-item"><span className="notif-icon">⚠️</span>Status perlu perhatian</div>
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">03</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 5 (odd) ── OpenClaw AI Agent */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · OpenClaw AI Agent</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">OpenClaw AI Agent</div>
                  <div className="page-divider"></div>
                  <div className="page-text">
                    <p>AIMS memanfaatkan <strong>OpenClaw AI Agent</strong> sebagai layanan otomatisasi yang berjalan pada sisi backend secara berkala tanpa memerlukan intervensi manual.</p>
                  </div>

                  <div className="page-subtitle">Fungsi Utama OpenClaw</div>
                  <ul className="feature-list" style={{marginBottom:'0.55em'}}>
                    <li>Evaluasi kondisi akademik berdasarkan aturan (rules engine)</li>
                    <li>Identifikasi mahasiswa yang memenuhi kriteria tertentu</li>
                    <li>Pembuatan rekomendasi tindak lanjut</li>
                    <li>Distribusi notifikasi kepada pengguna</li>
                  </ul>

                  <div className="page-subtitle">Kanal Notifikasi</div>
                  <div className="notif-grid">
                    <div className="notif-item"><span className="notif-icon">✈️</span>Telegram Bot</div>
                    <div className="notif-item"><span className="notif-icon">💬</span>WhatsApp</div>
                    <div className="notif-item"><span className="notif-icon">📧</span>Email</div>
                    <div className="notif-item"><span className="notif-icon">🔔</span>Kanal lainnya</div>
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">04</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 6 (even) ── Portal Pengguna */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Portal Pengguna</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Portal Pengguna</div>
                  <div className="page-divider"></div>
                  <div className="highlight-box">
                    <div className="hb-title">👑 Administrator &amp; Pimpinan</div>
                    Memantau statistik akademik · Distribusi tingkat risiko mahasiswa · Memberikan instruksi kepada Dosen PA · Mengirim notifikasi massal · Memonitor tindak lanjut
                  </div>
                  <div className="highlight-box">
                    <div className="hb-title">👨‍🏫 Dosen Penasehat Akademik</div>
                    Melihat daftar mahasiswa bimbingan · Memantau perkembangan akademik · Menerima tugas pembinaan · Mencatat hasil konsultasi · Memperbarui status pembinaan (audit trail)
                  </div>
                  <div className="highlight-box">
                    <div className="hb-title">🎓 Mahasiswa</div>
                    Riwayat IPS &amp; IPK · Grafik perkembangan akademik · Simulasi kelulusan · Status KRS &amp; pembayaran · Notifikasi akademik · Pengingat kegiatan
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">05</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 7 (odd) ── Arsitektur Sistem */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Arsitektur Sistem</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Arsitektur Sistem</div>
                  <div className="page-divider"></div>
                  <div className="page-text"><p>AIMS dikembangkan menggunakan arsitektur <strong>monorepo</strong> yang mengintegrasikan beberapa komponen utama:</p></div>
                  <div className="tech-stack">
                    <div className="tech-item"><strong>Frontend</strong>Next.js</div>
                    <div className="tech-item"><strong>Backend API</strong>FastAPI</div>
                    <div className="tech-item"><strong>Database</strong>PostgreSQL</div>
                    <div className="tech-item"><strong>Authentication</strong>JWT</div>
                    <div className="tech-item"><strong>AI Automation</strong>OpenClaw Agent</div>
                    <div className="tech-item"><strong>Scheduler</strong>APScheduler</div>
                    <div className="tech-item"><strong>Notification</strong>Telegram / WhatsApp</div>
                    <div className="tech-item"><strong>ORM</strong>SQLAlchemy</div>
                    <div className="tech-item"><strong>Migration</strong>Alembic</div>
                  </div>
                  <div className="page-subtitle" style={{marginTop:'0.55em'}}>Persyaratan Sistem</div>
                  <ul className="feature-list">
                    <li>Node.js 18 atau lebih baru</li>
                    <li>Python 3.12</li>
                    <li>PostgreSQL</li>
                    <li>Virtual Environment (venv) &amp; npm</li>
                  </ul>
                </div>
                <div className="page-footer">
                  <span className="page-num">06</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 8 (even) ── Setup & Akses */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Setup &amp; Akses</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Menjalankan Aplikasi</div>
                  <div className="page-divider"></div>
                  <div className="highlight-box">
                    <div className="hb-title">📦 Instalasi Dependensi</div>
                    <code style={{fontSize:'0.88em',color:'#6366f1',fontFamily:'Courier New, monospace'}}>npm install</code>
                  </div>
                  <div className="highlight-box">
                    <div className="hb-title">🚀 Jalankan Semua Layanan</div>
                    <code style={{fontSize:'0.88em',color:'#6366f1',fontFamily:'Courier New, monospace'}}>npm run dev</code>
                  </div>
                  <div className="page-subtitle" style={{marginTop:'0.3em'}}>Akses Aplikasi</div>
                  <table className="url-table">
                    <thead>
                      <tr><th>Layanan</th><th>URL</th></tr>
                    </thead>
                    <tbody>
                      <tr><td>Backend API</td><td><code>localhost:8000</code></td></tr>
                      <tr><td>Swagger API</td><td><code>localhost:8000/docs</code></td></tr>
                      <tr><td>Dashboard Mahasiswa</td><td><code>localhost:3000</code></td></tr>
                      <tr><td>Dashboard Administrator</td><td><code>localhost:3002</code></td></tr>
                    </tbody>
                  </table>
                </div>
                <div className="page-footer">
                  <span className="page-num">07</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 9 (odd) ── Fase 2: Mobile Platform */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Rencana Pengembangan</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Fase 2 – Academic Assistant</div>
                  <div className="page-divider"></div>
                  <div className="page-subtitle">Mobile Platform · Android &amp; iOS</div>
                  <div className="page-text">
                    <p>AIMS akan dikembangkan menjadi <strong>Academic Assistant</strong> berbentuk aplikasi mobile, sehingga mahasiswa, Dosen PA, serta pimpinan akademik dapat mengakses layanan kapan saja dan di mana saja melalui mekanisme <strong>real-time notification</strong>.</p>
                  </div>
                  <div className="page-subtitle">Tujuan Pengembangan</div>
                  <ul className="feature-list" style={{marginBottom:'0.5em'}}>
                    <li>Akses AIMS melalui perangkat Android dan iOS</li>
                    <li>Meningkatkan kecepatan penyampaian info akademik melalui push notification</li>
                    <li>Komunikasi lebih efektif antara mahasiswa, Dosen PA, dan Program Studi</li>
                    <li>Mengurangi keterlambatan penyampaian informasi penting</li>
                  </ul>
                  <div className="page-subtitle">Fitur Utama</div>
                  <ul className="feature-list">
                    <li>Jadwal perkuliahan real-time</li>
                    <li>Push notification akademik (KRS, UKT, jadwal ujian)</li>
                    <li>Kalender agenda akademik semester</li>
                    <li>Komunikasi PA (instruksi &amp; tindak lanjut)</li>
                    <li>Dashboard akademik personal (IPK, SKS, status)</li>
                  </ul>
                </div>
                <div className="page-footer">
                  <span className="page-num">08</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 10 (even) ── Fase 3: Learning Platform */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Rencana Pengembangan</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Fase 3 – Collaborative Learning</div>
                  <div className="page-divider"></div>
                  <div className="page-subtitle">Collaborative Learning Platform</div>
                  <div className="page-text">
                    <p>AIMS dikembangkan menjadi <strong>Collaborative Learning Platform</strong> yang mengintegrasikan LMS dengan pendekatan social learning. Setiap mata kuliah memiliki <strong>Learning Feed</strong> sebagai ruang interaksi digital kolaboratif.</p>
                  </div>
                  <div className="page-subtitle">Learning Feed Mata Kuliah</div>
                  <ul className="feature-list" style={{marginBottom:'0.45em'}}>
                    <li>Penyampaian pengumuman &amp; materi pembelajaran</li>
                    <li>Diskusi akademik antara dosen dan mahasiswa</li>
                    <li>Pemberian &amp; pengumpulan tugas berbasis feed</li>
                    <li>Umpan balik dan penilaian dari dosen</li>
                    <li>Interaksi: komentar, like, balasan, diskusi lanjutan</li>
                  </ul>
                  <div className="page-subtitle">Aktivitas Mahasiswa</div>
                  <ul className="feature-list">
                    <li>Mengajukan pertanyaan mengenai materi kuliah</li>
                    <li>Berbagi referensi ilmiah &amp; solusi studi kasus</li>
                    <li>Diskusi kolaboratif sesama mahasiswa</li>
                  </ul>
                </div>
                <div className="page-footer">
                  <span className="page-num">09</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 11 (odd) ── Manfaat & Penutup */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Manfaat &amp; Visi</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Manfaat &amp; Visi ke Depan</div>
                  <div className="page-divider"></div>

                  <div className="roadmap-phase">
                    <div className="phase-label">Fase 2 · Mobile</div>
                    <div className="phase-title">Academic Assistant</div>
                    <div className="phase-desc">AIMS berkembang menjadi <em>pendamping akademik digital</em> yang secara proaktif membantu mahasiswa dan dosen mengelola aktivitas akademik sehari-hari — cepat, personal, dan selalu terhubung.</div>
                  </div>

                  <div className="roadmap-phase">
                    <div className="phase-label">Fase 3 · Learning</div>
                    <div className="phase-title">Collaborative Learning Platform</div>
                    <div className="phase-desc">AIMS berkembang dari sistem monitoring akademik menjadi <em>platform pembelajaran kolaboratif</em> yang mengintegrasikan administrasi akademik, komunikasi, dan aktivitas belajar dalam satu ekosistem digital.</div>
                  </div>

                  <div className="page-text" style={{marginTop:'0.4em',fontStyle:'italic',color:'#6b7280',fontSize:'clamp(0.43em,0.88vw,0.66em)'}}>
                    Dengan tiga fase pengembangan ini, AIMS bertransformasi dari sistem monitoring menjadi ekosistem akademik digital yang komprehensif dan terpadu.
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">10</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 12 (even) ── Back Cover POLOS/BLANK */}
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
