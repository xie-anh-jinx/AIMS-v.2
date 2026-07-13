/**
 * fetch_missing_prodi.js
 * ─────────────────────
 * Fetch data PA + Mahasiswa untuk 6 prodi yang belum ada di dump lokal:
 * Sastra Arab, Sastra Inggris, Sastra Indonesia, Arkeologi, Sastra Mandarin,
 * Kajian Budaya S2, Linguistik S2
 *
 * Gunakan token langsung dari .env (NEOSIA_TOKEN) sehingga tidak perlu
 * browser/Playwright. Simpan hasil ke pa_dump_missing.json lalu skrip Python
 * akan memprosesnya ke DB.
 *
 * Jalankan: node plugins/academic-connector/fetch_missing_prodi.js
 */

import * as fs from 'fs';
import * as dotenv from 'dotenv';
dotenv.config({ path: '../../.env' });

const BASE_URL = 'https://api.neosia.unhas.ac.id';
const TOKEN    = process.env.NEOSIA_TOKEN;
const OUT_FILE = './pa_dump_missing.json';

if (!TOKEN) {
    console.error('[ERROR] NEOSIA_TOKEN tidak ditemukan di .env');
    process.exit(1);
}

const headers = {
    'Authorization': `Bearer ${TOKEN}`,
    'Accept': 'application/json',
    'Content-Type': 'application/json',
};

async function apiGet(path) {
    const url = `${BASE_URL}${path}`;
    const res  = await fetch(url, { headers });
    if (!res.ok) {
        throw new Error(`HTTP ${res.status} on ${path}`);
    }
    return res.json();
}

/** Ambil semua semester aktif yang tersedia */
async function getSemesters() {
    const r = await apiGet('/api/semester');
    const arr = r.data ?? r ?? [];
    // Ambil 4 semester terakhir terbaru saja
    return arr.sort((a, b) => b.id - a.id).slice(0, 4);
}

/** Ambil daftar prodi dari endpoint */
async function getProdi() {
    const r = await apiGet('/api/prodi?page=1&perPage=100');
    return r.data ?? r ?? [];
}

/** Ambil daftar PA + mahasiswanya untuk satu semester */
async function fetchPAForSemester(idSemester) {
    const endpoint = `/api/penasihat_akademik?id_semester=${idSemester}&page=1&perPage=999`;
    const r = await apiGet(endpoint);
    
    let arr = r;
    if (r && typeof r === 'object' && !Array.isArray(r)) {
        arr = r.data ?? r.penasihat_akademiks ?? r.penasihatAkademiks ?? r.items ?? 
              r.list ?? r.dosen ?? Object.values(r).find(v => Array.isArray(v)) ?? [];
    }
    return Array.isArray(arr) ? arr : [];
}

const TARGET_PRODI_KEYWORDS = [
    'SASTRA ARAB',
    'SASTRA INGGRIS',
    'SASTRA INDONESIA',
    'ARKEOLOGI',
    'MANDARIN',
    'KAJIAN BUDAYA',
    'LINGUISTIK',
    'SASTRA DAERAH - S',
    'ILMU SEJARAH - S',
    'SASTRA JEPANG - S',
    'SASTRA PRANCIS - S',
    'PARIWISATA',
];

async function main() {
    console.log('[INFO] Memulai fetch data prodi yang belum ada …');
    
    // Test koneksi
    try {
        const testRes = await apiGet('/api/semester');
        console.log('[INFO] Koneksi ke Neosia berhasil ✓');
    } catch(e) {
        console.error(`[ERROR] Gagal terhubung ke Neosia: ${e.message}`);
        console.log('[INFO] Mencoba endpoint alternatif…');
    }

    let semesters = [];
    try {
        semesters = await getSemesters();
        console.log(`[INFO] Semester tersedia: ${semesters.map(s => s.nama ?? s.id).join(', ')}`);
    } catch(e) {
        console.error('[WARN] Gagal ambil daftar semester:', e.message);
        // Gunakan ID semester yang diketahui dari sesi sebelumnya
        semesters = [{ id: 4036 }, { id: 4035 }, { id: 4034 }];
    }

    const allPaRecords = [];
    const seenDosenId  = new Map(); // dosenId → index di allPaRecords

    for (const sem of semesters) {
        const semId = sem.id;
        console.log(`\n[SEM ${semId}] Fetching PA list …`);
        
        try {
            const paList = await fetchPAForSemester(semId);
            console.log(`  → Ditemukan ${paList.length} PA object`);
            
            for (const paObj of paList) {
                const dosen = paObj.dosen ?? paObj;
                const id    = dosen.id ?? dosen.nip ?? dosen.nidn;
                const mahasiswas = paObj.mahasiswas ?? paObj.bimbingan ?? [];
                
                if (!id) continue;
                
                if (seenDosenId.has(id)) {
                    // Gabungkan mahasiswa yang belum ada
                    const existing = allPaRecords[seenDosenId.get(id)];
                    const existingNims = new Set(
                        existing.mahasiswas.map(m => typeof m === 'string' ? m : m.nim)
                    );
                    for (const mhs of mahasiswas) {
                        const nim = typeof mhs === 'string' ? mhs : mhs.nim;
                        if (!existingNims.has(nim)) {
                            existing.mahasiswas.push(mhs);
                            existingNims.add(nim);
                        }
                    }
                } else {
                    seenDosenId.set(id, allPaRecords.length);
                    allPaRecords.push({ dosen, mahasiswas: [...mahasiswas] });
                }
            }
        } catch(e) {
            console.error(`  [WARN] Gagal fetch semester ${semId}: ${e.message}`);
        }
    }

    console.log(`\n[INFO] Total PA unik terkumpul: ${allPaRecords.length}`);
    
    // Hitung mahasiswa unik
    const allNims = new Set();
    for (const rec of allPaRecords) {
        for (const mhs of rec.mahasiswas) {
            const nim = typeof mhs === 'string' ? mhs : mhs?.nim;
            if (nim) allNims.add(nim);
        }
    }
    console.log(`[INFO] Total mahasiswa unik: ${allNims.size}`);

    // Gabung dengan dump lama jika ada
    let existingDump = [];
    const mainDumpPath = './pa_dump_all.json';
    if (fs.existsSync(mainDumpPath)) {
        console.log('[INFO] Menggabungkan dengan dump lama (pa_dump_all.json)…');
        existingDump = JSON.parse(fs.readFileSync(mainDumpPath, 'utf8'));
    }

    // Merged: cek apakah PA sudah ada di dump lama
    const existingDosenIds = new Set(
        existingDump.map(r => r.dosen?.id ?? r.dosen?.nip ?? r.dosen?.nidn)
    );
    
    const newOnly = allPaRecords.filter(r => {
        const id = r.dosen?.id ?? r.dosen?.nip ?? r.dosen?.nidn;
        return !existingDosenIds.has(id);
    });

    console.log(`[INFO] PA baru (belum di dump lama): ${newOnly.length}`);
    
    // Simpan SEMUA (lama + baru) ke pa_dump_all.json sebagai cadangan terkonsolidasi
    const merged = [...existingDump, ...newOnly];
    fs.writeFileSync(mainDumpPath, JSON.stringify(merged), 'utf8');
    console.log(`[INFO] pa_dump_all.json diperbarui: ${merged.length} PA total`);
    
    // Juga simpan yang baru saja ke file terpisah
    fs.writeFileSync(OUT_FILE, JSON.stringify(allPaRecords), 'utf8');
    console.log(`[INFO] pa_dump_missing.json tersimpan: ${allPaRecords.length} PA`);
    
    console.log('\n[DONE] Selesai. Jalankan sync_neosia_to_db.py untuk memasukkan ke database.');
}

main().catch(err => {
    console.error('[FATAL]', err.message);
    process.exit(1);
});
