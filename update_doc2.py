import re

with open('apps/frontend/src/app/documentation/page.tsx', 'r') as f:
    content = f.read()

new_pages = """            {/* ── PAGE 1 (odd) ── Cover Depan */}
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

            {/* ── PAGE 2 (even) ── Pendahuluan */}
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
                    <p><strong>Academic Intelligence Management System (AIMS)</strong> merupakan platform manajemen informasi akademik yang dikembangkan untuk mendukung pengelolaan administrasi akademik, pemantauan perkembangan studi mahasiswa, serta otomatisasi berbagai proses akademik melalui pemanfaatan Artificial Intelligence (AI).</p>
                    <p>AIMS <strong>tidak dirancang untuk menggantikan NeoSIA</strong> sebagai Sistem Informasi Akademik utama Universitas Hasanuddin. Sebaliknya, AIMS berfungsi sebagai <strong>Companion Application</strong> yang memperluas kemampuan NeoSIA melalui penyediaan dashboard pemantauan, layanan AI, Learning Feed, notifikasi otomatis, serta analisis akademik berbasis data.</p>
                  </div>
                  <div className="warning-box" style={{marginTop: '0.5em'}}>
                    <div className="hb-title">Sinkronisasi Satu Arah</div>
                    Melalui mekanisme sinkronisasi data satu arah (read-only), seluruh data akademik tetap dikelola oleh NeoSIA sebagai sumber data utama (single source of truth), sedangkan AIMS memanfaatkan data tersebut untuk menghasilkan layanan yang lebih proaktif, informatif, dan mendukung proses pengambilan keputusan.
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">02</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 3 (odd) ── Visi & Misi */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Visi & Misi</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Visi & Misi</div>
                  <div className="page-divider"></div>
                  
                  <div className="page-subtitle">Visi</div>
                  <div className="page-text" style={{fontStyle: 'italic', marginBottom: '1em'}}>
                    "Menjadi platform Academic Intelligence yang mampu mendukung transformasi digital Fakultas Ilmu Budaya Universitas Hasanuddin melalui pemanfaatan Artificial Intelligence, analisis data, dan otomatisasi layanan akademik."
                  </div>

                  <div className="page-subtitle">Misi</div>
                  <ul className="feature-list">
                    <li>Meningkatkan kualitas layanan akademik.</li>
                    <li>Mempermudah pemantauan perkembangan studi mahasiswa.</li>
                    <li>Mendukung proses pembimbingan akademik.</li>
                    <li>Mengurangi beban administrasi dosen.</li>
                    <li>Menyediakan dashboard analitik bagi pimpinan.</li>
                    <li>Mengimplementasikan Artificial Intelligence pada layanan akademik.</li>
                  </ul>
                </div>
                <div className="page-footer">
                  <span className="page-num">03</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 4 (even) ── Konsep AIMS */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Konsep Sistem</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Konsep Utama AIMS</div>
                  <div className="page-divider"></div>
                  
                  <div className="page-subtitle">1. Academic Monitoring</div>
                  <div className="page-text" style={{marginBottom: '0.5em'}}>
                    Memantau perkembangan akademik berkala (IPS, IPK, SKS, Kehadiran, Status, Riwayat Kuliah, Learning Feed). Monitoring otomatis membantu dosen dan pengelola mengetahui kondisi tanpa pemeriksaan manual.
                  </div>

                  <div className="page-subtitle">2. Academic Intelligence</div>
                  <div className="page-text" style={{marginBottom: '0.5em'}}>
                    Memanfaatkan AI untuk analisis studi, identifikasi mahasiswa berisiko (Early Warning System), rekomendasi ke PA, serta AI Assistant bagi dosen dan mahasiswa. Mendukung pengambilan keputusan berbasis data.
                  </div>

                  <div className="page-subtitle">3. Academic Automation</div>
                  <div className="page-text">
                    Mengotomatisasi proses akademik seperti pengingat KRS & UKT, notifikasi penurunan IPK, jadwal konsultasi, reminder presensi, dan penyusunan laporan otomatis.
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">04</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 5 (odd) ── Ekosistem Akademik */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Ekosistem Akademik</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Posisi AIMS</div>
                  <div className="page-divider"></div>
                  
                  <div className="page-text" style={{display: 'flex', justifyContent: 'center', marginBottom: '0.5em'}}>
                    <div style={{fontFamily: 'monospace', fontSize: 'clamp(0.55em, 1vw, 0.7em)', lineHeight: '1.2', background: 'rgba(99,102,241,0.05)', padding: '1em', borderRadius: '8px', border: '1px solid rgba(99,102,241,0.2)', color: '#374151', whiteSpace: 'pre'}}>
{`        Mahasiswa
            │
    ┌───────▼────────┐
    │     NeoSIA     │
    │ Sistem Akademik│
    └───────┬────────┘
            │
    Sinkronisasi Data
       (Read Only)
            │
            ▼
┌────────────────────────┐
│          AIMS          │
│  Academic Intelligence │
└────────────────────────┘
    │       │        │
    ▼       ▼        ▼
Dashboard  AI Agent  Feed
    │
    ▼
 Notification Service`}
                    </div>
                  </div>
                  
                  <div className="page-text" style={{fontSize: '0.7em'}}>
                    <p>NeoSIA tetap menjadi sistem utama yang bertanggung jawab terhadap pengelolaan data akademik. AIMS memanfaatkan data tersebut untuk menyediakan berbagai layanan tambahan tanpa mengubah mekanisme akademik yang telah berjalan.</p>
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">05</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 6 (even) ── Tujuan & Karakteristik */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Tujuan & Karakteristik</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Tujuan Pengembangan</div>
                  <div className="page-divider"></div>
                  <ul className="feature-list" style={{marginBottom: '1em'}}>
                    <li>Meningkatkan kualitas pelayanan akademik.</li>
                    <li>Menyediakan sistem monitoring mahasiswa secara real-time.</li>
                    <li>Mendukung proses pembimbingan akademik.</li>
                    <li>Mempercepat penyampaian informasi akademik.</li>
                    <li>Mengotomatisasi administrasi akademik.</li>
                    <li>Membantu pimpinan dalam pengambilan keputusan.</li>
                    <li>Menghadirkan layanan Artificial Intelligence dalam lingkungan akademik.</li>
                  </ul>

                  <div className="page-main-title">Karakteristik Sistem</div>
                  <div className="page-divider"></div>
                  <table className="url-table">
                    <tbody>
                      <tr><th>Companion App</th><td>Berjalan berdampingan dengan NeoSIA</td></tr>
                      <tr><th>Read Only Data</th><td>Tidak mengubah data pada sistem induk</td></tr>
                      <tr><th>Academic AI</th><td>Menggunakan AI untuk analisis akademik</td></tr>
                      <tr><th>Early Warning</th><td>Deteksi dini permasalahan akademik</td></tr>
                      <tr><th>Learning Feed</th><td>Pembelajaran berbasis media sosial</td></tr>
                      <tr><th>Automation</th><td>Administrasi akademik otomatis</td></tr>
                    </tbody>
                  </table>
                </div>
                <div className="page-footer">
                  <span className="page-num">06</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 7 (odd) ── Manfaat I */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Manfaat</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Manfaat (Bagian I)</div>
                  <div className="page-divider"></div>

                  <div className="highlight-box">
                    <div className="hb-title">🎓 Bagi Mahasiswa</div>
                    <ul className="feature-list" style={{marginTop: '0.3em'}}>
                      <li>Informasi akademik terpusat.</li>
                      <li>AI Assistant untuk membantu perkuliahan.</li>
                      <li>Monitoring perkembangan studi secara mandiri.</li>
                      <li>Pengingat otomatis berbagai aktivitas akademik.</li>
                      <li>Learning Feed yang interaktif.</li>
                    </ul>
                  </div>

                  <div className="highlight-box">
                    <div className="hb-title">👨‍🏫 Bagi Dosen & PA</div>
                    <ul className="feature-list" style={{marginTop: '0.3em'}}>
                      <li>Monitoring mahasiswa perwalian yang proaktif.</li>
                      <li>Pencatatan riwayat konsultasi terpadu.</li>
                      <li>Learning Feed untuk kelas.</li>
                      <li>AI Assistant pendukung pengajaran.</li>
                      <li>Ringkasan otomatis aktivitas mahasiswa.</li>
                    </ul>
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">07</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 8 (even) ── Manfaat II */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Manfaat</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Manfaat (Bagian II)</div>
                  <div className="page-divider"></div>

                  <div className="roadmap-phase">
                    <div className="phase-label">Tingkat Fakultas</div>
                    <div className="phase-title">Bagi Fakultas</div>
                    <div className="phase-desc">
                      <ul className="feature-list" style={{marginTop: '0.3em'}}>
                        <li>Dashboard pemantauan akademik komprehensif.</li>
                        <li>Monitoring seluruh mahasiswa di tingkat fakultas.</li>
                        <li>Evaluasi akademik berbasis data.</li>
                        <li>Laporan perkembangan akademik otomatis.</li>
                        <li>Penyediaan data valid untuk pengambilan keputusan.</li>
                      </ul>
                    </div>
                  </div>

                  <div className="roadmap-phase">
                    <div className="phase-label">Tingkat Pimpinan</div>
                    <div className="phase-title">Bagi Pimpinan</div>
                    <div className="phase-desc">
                      <ul className="feature-list" style={{marginTop: '0.3em'}}>
                        <li>Dashboard Executive real-time.</li>
                        <li>Academic Analytics dan peramalan tren.</li>
                        <li>Early Warning System di tingkat institusi.</li>
                        <li>Statistik akademik terperinci dan akurat.</li>
                        <li>Monitoring kesehatan institusi secara keseluruhan.</li>
                      </ul>
                    </div>
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">08</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 9 (odd) ── Back Cover POLOS/BLANK */}
            <div className="book-page back-cover-blank">
              <div className="page-content">
              </div>
            </div>

            {/* ── PAGE 10 (even) ── Back Cover POLOS/BLANK */}
            <div className="book-page back-cover-blank">
              <div className="page-content">
              </div>
            </div>
"""

start_str = '            {/* ── PAGE 1 (odd) ── Cover Depan */}'
end_str = '          </div>\n        </div>\n      </div>\n    </>\n  );\n}'

start_idx = content.find(start_str)
end_idx = content.find(end_str)

new_content = content[:start_idx] + new_pages + '\n' + content[end_idx:]

with open('apps/frontend/src/app/documentation/page.tsx', 'w') as f:
    f.write(new_content)
