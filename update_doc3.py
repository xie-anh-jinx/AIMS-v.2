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
"""

start_str = '            {/* ── PAGE 1 (odd) ── Cover Depan */}'
end_str = '          </div>\n        </div>\n      </div>\n    </>\n  );\n}'

start_idx = content.find(start_str)
end_idx = content.find(end_str)

new_content = content[:start_idx] + new_pages + '\n' + content[end_idx:]

with open('apps/frontend/src/app/documentation/page.tsx', 'w') as f:
    f.write(new_content)
