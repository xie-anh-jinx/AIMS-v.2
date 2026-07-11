import fs from 'fs';
import fetch from 'node-fetch'; // fetch node 18 bawaan gak masalah tapi biar eksplisit
import { DatabaseAdapter } from './src/adapters/DatabaseAdapter.js';
import { config } from 'dotenv';
config({ path: '../../.env' }); // Root Env

const logger = { info: console.log, warn: console.warn, error: console.error, debug: () => {} };

async function fetchWithRetry(url, options, retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            const res = await fetch(url, options);
            if (res.ok) return await res.json();
            return null;
        } catch (e) {
            if (i === retries - 1) return null;
            await new Promise(r => setTimeout(r, 1000));
        }
    }
}

async function syncPA() {
    const db = new DatabaseAdapter(process.env.DATABASE_URL, logger);
    const BASE_URL = 'https://api.neosia.unhas.ac.id';
    
    const accounts = ['fib_pariwisata', 'fib_sas_prancis', 'fib_sas_jepang', 'fib_sas_daerah', 'fib_ilmu_sejarah'];
    let token = null;

    for (const acc of accounts) {
        const sessionFile = `./providers/${acc}/session.json`;
        if (fs.existsSync(sessionFile)) {
            try {
                const data = JSON.parse(fs.readFileSync(sessionFile, 'utf8'));
                if (data.bearerToken) { token = data.bearerToken; break; }
            } catch(e) {}
        }
    }

    if (!token) {
        console.log("[ERROR] Tidak ada token auth tersimpan.");
        process.exit(1);
    }
    
    const headers = { Authorization: `Bearer ${token}`, Accept: 'application/json' };
    console.log(`[OK] Using token. Fetching PA...`);

    const psJson = await fetchWithRetry(`${BASE_URL}/api/admin/prodi_semester?filters[is_used]=1`, { headers });
    const psList = psJson?.prodiSemesters || psJson?.data || [];
    
    console.log(`[INFO] Found ${psList.length} prodi_semester aktif.`);
    
    const client = await db.pool.connect();
    // KEEP user ID so we don't break old bindings if any, but clean mockup
    await client.query("DELETE FROM users WHERE role = 'ADVISOR' AND username LIKE 'PA_%'");
    const hashed = '$2b$12$FCMiEQZ3wTWHR8oa47TE4ODtJUoiI/Tger84vjJsS6GAbAa/m5bVS'; // password123
    client.release();

    let totalDosen = 0;
    let totalMhs = 0;

    for (const ps of psList) {
        const idSem = ps.id || ps.id_prodi_semester;
        if (!idSem) continue;

        const data = await fetchWithRetry(`${BASE_URL}/api/admin/penasihat_akademik?filters[id_prodi_semester]=${idSem}`, { headers });
        if (!data) continue;

        const paArray = data.dosens || data.penasihat_akademiks || data.penasihatAkademiks || data.data || [];
        
        for (const paObj of paArray) {
            const d = paObj.dosen || paObj;
            const nip = (d.nip || d.id_pegawai || d.username)?.toString();
            const nama = d.nama_dosen || d.nama || d.nama_pegawai;
            
            if (!nip) continue;
            
            const advId = await db.upsertAdvisor(nip, nama);
            // enforce password123
            await db.pool.query("UPDATE users SET hashed_password = $1 WHERE username = $2", [hashed, nip]);
            totalDosen++;

            const mahasiswas = paObj.mahasiswas || paObj.mahasiswa || paObj.bimbingan || [];
            const iterMhs = Array.isArray(mahasiswas) ? mahasiswas : [mahasiswas];
            for (const m of iterMhs) {
                const nim = (typeof m === 'string' ? m : (m.nim || m.id))?.toString();
                if (nim) {
                    try {
                        await db.assignAdvisor(nim, advId);
                        totalMhs++;
                    } catch(e) {} 
                }
            }
        }
    }
    
    console.log(`\n============== SYNC PA SELESAI ==============`);
    console.log(`Total Dosen PA disinkronkan: ${totalDosen}`);
    console.log(`Total Relasi Mahasiswa berhasil diikat di Database: ${totalMhs}`);
    process.exit(0);
}
syncPA();
