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
                    Platform pendukung sistem informasi akademik untuk pemantauan proaktif perkembangan mahasiswa
                  </div>
                  <div className="cover-meta">Dokumentasi Sistem · Versi 2.0</div>
                </div>
              </div>
            </div>

            {/* ── PAGE 2 (even) ── Pengantar & Dashboard */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Pengantar</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Dokumentasi Fitur AIMS</div>
                  <div className="page-divider"></div>
                  <div className="page-text">
                    <p><strong>AIMS (Academic Intelligence Management System)</strong> adalah platform manajemen akademik berbasis kecerdasan buatan (AI) yang dirancang untuk memberikan pengalaman perkuliahan yang interaktif, seamless, dan canggih bagi mahasiswa, dosen, serta penasihat akademik.</p>
                  </div>
                  
                  <div className="page-subtitle">1. Dashboard Utama (AIMS Portal)</div>
                  <div className="page-text">
                    <p>Pusat kontrol utama bagi setiap pengguna setelah berhasil masuk (login).</p>
                  </div>
                  <ul className="feature-list">
                    <li><strong>Multi-Role Access:</strong> Mendukung peran berbeda seperti STUDENT, LECTURER, dan ADVISOR dengan tingkat akses yang disesuaikan.</li>
                    <li><strong>Daftar Kelas Aktif:</strong> Menampilkan semua mata kuliah beserta ringkasan jadwal dan progres kehadiran.</li>
                    <li><strong>Statistik Akademik:</strong> Menampilkan IPK, SKS, dan grafik performa akademik secara keseluruhan.</li>
                  </ul>
                </div>
                <div className="page-footer">
                  <span className="page-num">02</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 3 (odd) ── Kelas & Absensi */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Kelas Terpadu</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">2. Kelas & Mata Kuliah</div>
                  <div className="page-divider"></div>
                  <div className="page-text">
                    <p>Setiap mata kuliah memiliki halaman interaktif yang dibagi menjadi beberapa tab:</p>
                  </div>

                  <div className="page-subtitle">A. Informasi Kelas</div>
                  <ul className="feature-list" style={{marginBottom: '0.4em'}}>
                    <li>Menampilkan deskripsi, SKS, jadwal, ruang kelas, serta dosen pengampu.</li>
                  </ul>

                  <div className="page-subtitle">B. Absensi Pintar (Audio Token)</div>
                  <div className="page-text">
                    <p>Sistem presensi revolusioner tanpa ketik PIN atau scan barcode.</p>
                  </div>
                  <ul className="feature-list">
                    <li><strong>Sisi Dosen:</strong> Menekan "Mulai Sesi", perangkat dosen mendengarkan gelombang suara di ruangan.</li>
                    <li><strong>Sisi Mahasiswa:</strong> Menekan "Pancarkan Audio Token", memancarkan suara ultrasonik.</li>
                    <li><strong>Auto-Discovery:</strong> Sistem mencocokkan jadwal otomatis, presensi dicatat real-time (Mencegah penitipan absen berkat Device Binding).</li>
                  </ul>
                </div>
                <div className="page-footer">
                  <span className="page-num">03</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 4 (even) ── Modul & AI Chat */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Modul & AI</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Interaksi & AI Assistant</div>
                  <div className="page-divider"></div>

                  <div className="page-subtitle">C. Modul & Tugas (Interactive Feed)</div>
                  <div className="page-text"><p>Ruang diskusi ala media sosial untuk akademik.</p></div>
                  <ul className="feature-list" style={{marginBottom: '0.4em'}}>
                    <li><strong>Post & Modul:</strong> Unggah materi, tugas, pengumuman.</li>
                    <li><strong>Lampiran:</strong> Dukungan berbagai format file.</li>
                    <li><strong>Interaksi:</strong> Diskusi asinkronus via komentar dan like.</li>
                  </ul>

                  <div className="page-subtitle">D. Obrolan AI (Course Chatbot)</div>
                  <div className="page-text"><p>Asisten AI spesifik mata kuliah (24/7).</p></div>
                  <ul className="feature-list" style={{marginBottom: '0.4em'}}>
                    <li>Menjawab seputar silabus, materi, atau klarifikasi tugas.</li>
                    <li>Memiliki konteks penuh terhadap kurikulum kelas.</li>
                  </ul>

                  <div className="page-subtitle">E. Anggota (Members)</div>
                  <ul className="feature-list">
                    <li>Direktori lengkap dosen pengampu dan mahasiswa terdaftar.</li>
                  </ul>
                </div>
                <div className="page-footer">
                  <span className="page-num">04</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 5 (odd) ── Notifikasi & Keamanan */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Notifikasi & Arsitektur</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Notifikasi & Keamanan</div>
                  <div className="page-divider"></div>

                  <div className="page-subtitle">3. Notifikasi Cerdas (Telegram Bot)</div>
                  <ul className="feature-list" style={{marginBottom: '0.6em'}}>
                    <li>Integrasi real-time mengirimkan notifikasi tugas baru, perubahan jadwal, dan reminder secara instan ke ponsel.</li>
                    <li>Pengguna dapat menghubungkan akun AIMS mereka dengan mudah.</li>
                  </ul>

                  <div className="page-subtitle">4. Keamanan & Arsitektur</div>
                  <ul className="feature-list">
                    <li><strong>JWT Auth:</strong> Sistem login token-based yang aman.</li>
                    <li><strong>Device Binding:</strong> Absensi terkunci pada perangkat mahasiswa terdaftar (device_uuid).</li>
                    <li><strong>Modern Stack:</strong> Menggunakan <em>Next.js</em> untuk antarmuka yang sangat responsif, dan <em>FastAPI</em> di backend untuk memproses logika AI dan pemrosesan Audio tingkat tinggi.</li>
                  </ul>
                </div>
                <div className="page-footer">
                  <span className="page-num">05</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 6 (even) ── Tujuan & Keunggulan */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Early Warning System</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Tujuan & Keunggulan</div>
                  <div className="page-divider"></div>
                  <div className="page-text">
                    <p>AIMS juga meningkatkan efektivitas pembinaan akademik melalui <strong>early warning system</strong>.</p>
                  </div>

                  <div className="page-subtitle">Deteksi Dini Mahasiswa Berisiko</div>
                  <div className="page-text"><p>Klasifikasi risiko akademik mahasiswa secara otomatis:</p></div>
                  <div className="zone-badges">
                    <span className="zone-badge zone-safe">🟢 Zona Aman</span>
                    <span className="zone-badge zone-warn">🟡 Zona Perhatian</span>
                    <span className="zone-badge zone-danger">🔴 Zona Risiko Tinggi</span>
                  </div>

                  <div className="page-subtitle" style={{marginTop:'0.5em'}}>Batas SKS & Masa Studi Maksimal</div>
                  <div className="notif-grid" style={{gridTemplateColumns:'1fr'}}>
                    <div className="notif-item" style={{justifyContent:'space-between', fontSize:'0.75em'}}>
                      <span>🎓 <strong>S1</strong>: Min <strong>144 SKS</strong></span>
                      <span>Maks <strong>14 Smt</strong></span>
                    </div>
                    <div className="notif-item" style={{justifyContent:'space-between', fontSize:'0.75em'}}>
                      <span>🎓 <strong>S2</strong>: Min <strong>46 SKS</strong></span>
                      <span>Maks <strong>6 Smt</strong></span>
                    </div>
                    <div className="notif-item" style={{justifyContent:'space-between', fontSize:'0.75em'}}>
                      <span>🎓 <strong>S3</strong>: Min <strong>65 SKS</strong></span>
                      <span>Maks <strong>10 Smt</strong></span>
                    </div>
                  </div>
                </div>
                <div className="page-footer">
                  <span className="page-num">06</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 7 (odd) ── Kebijakan Data */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Kebijakan Data</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Kebijakan Kedaulatan Data</div>
                  <div className="page-divider"></div>
                  <div className="warning-box">
                    <div className="hb-title">⚠ Penting</div>
                    Seluruh data riwayat akademik mahasiswa disinkronkan secara <strong>satu arah (read-only)</strong> dari sistem akademik induk Universitas (NeoSIA).
                  </div>
                  <div className="page-subtitle">Batasan Kewenangan</div>
                  <ul className="feature-list" style={{marginBottom:'0.55em'}}>
                    <li>AIMS tidak mengubah atau menghapus data nilai asli pada sistem induk.</li>
                    <li>Seluruh perubahan transkrip tetap diproses melalui birokrasi universitas.</li>
                  </ul>
                  <div className="page-subtitle">Nilai Tambah AIMS</div>
                  <ul className="feature-list">
                    <li>Visualisasi dan analitik data akademik</li>
                    <li>Sistem pelacakan koordinasi PA</li>
                    <li>Platform pembelajaran dan interaksi kelas modern</li>
                  </ul>
                </div>
                <div className="page-footer">
                  <span className="page-num">07</span>
                  <span className="page-watermark">AIMS · 2024</span>
                </div>
              </div>
            </div>

            {/* ── PAGE 8 (even) ── Visi & Manfaat */}
            <div className="book-page">
              <div className="page-content">
                <div className="page-header">
                  <div className="logo-mark">A</div>
                  <span className="page-header-title">AIMS · Visi ke Depan</span>
                </div>
                <div className="page-body">
                  <div className="page-main-title">Visi & Pengembangan</div>
                  <div className="page-divider"></div>

                  <div className="roadmap-phase">
                    <div className="phase-label">Fase 2 · Mobile First</div>
                    <div className="phase-title">Academic Assistant</div>
                    <div className="phase-desc">AIMS akan segera dirilis sebagai aplikasi Native untuk mendampingi mahasiswa secara proaktif (notifikasi jadwal, pengingat KRS, tagihan, dll).</div>
                  </div>

                  <div className="roadmap-phase">
                    <div className="phase-label">Fase 3 · Ekosistem Terpadu</div>
                    <div className="phase-title">Smart Campus Eco-System</div>
                    <div className="phase-desc">AIMS berkembang dari sebatas platform ke sebuah ekosistem cerdas yang mengintegrasikan semua kebutuhan administratif, sosial, dan akademik mahasiswa.</div>
                  </div>

                  <div className="page-text" style={{marginTop:'0.4em',fontStyle:'italic',color:'#6b7280',fontSize:'clamp(0.43em,0.88vw,0.66em)'}}>
                    Dengan integrasi kuat AI dan UI interaktif, AIMS menjadi pondasi utama smart university di masa depan.
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
"""

start_str = '            {/* ── PAGE 1 (odd) ── Cover Depan */}'
end_str = '          </div>\n        </div>\n      </div>\n    </>\n  );\n}'

start_idx = content.find(start_str)
end_idx = content.find(end_str)

new_content = content[:start_idx] + new_pages + '\n' + content[end_idx:]

with open('apps/frontend/src/app/documentation/page.tsx', 'w') as f:
    f.write(new_content)
