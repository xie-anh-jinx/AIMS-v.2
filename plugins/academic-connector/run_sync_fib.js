import fs from 'fs';
import YAML from 'yaml';
import { AcademicConnector } from './src/AcademicConnector.js';
import { DatabaseAdapter } from './src/adapters/DatabaseAdapter.js';
import { config } from 'dotenv';

config({ path: '../../.env' }); // Root Env
const logger = { info: console.log, warn: console.warn, error: console.error, debug: () => {} };

const configRaw = fs.readFileSync('./config.yml', 'utf8');
const appConfig = YAML.parse(configRaw);

async function run() {
    console.log("=== MEMULAI SINKRONISASI PA SE-FAKULTAS ILMU BUDAYA ===");
    
    // 1. Get Token via Playwright
    const connector = new AcademicConnector();
    connector.restAdapter.baseUrl = 'https://api.neosia.unhas.ac.id';
    
    const account = appConfig.accounts.find(a => a.id === "fib_superadmin");
    console.log(`[1] Login Playwright untuk ${account.program_studi}...`);
    
    const tokens = await connector.browserAdapter.captureSessionToken(account);
    if (!tokens || !tokens.bearerToken) {
        console.error(`[ERROR] Gagal mendapatkan bearer Token dari Neosia!`);
        process.exit(1);
    }
    const token = tokens.bearerToken;
    console.log(`[OK] Bearer token berhasil ditangkap.`);

    // 2. Begin API Sync
    const db = new DatabaseAdapter(process.env.DATABASE_URL, logger);
    const BASE_URL = 'https://api.neosia.unhas.ac.id';
    
    console.log(`[2] Fetching active semesters...`);
    // ALWAYS USE connector.restAdapter to get perfect Axios unwrap instead of raw fetch
    const psUrl = `${BASE_URL}/api/admin/prodi_semester?filters[is_used]=1`;
    let psData = null;
    try {
        psData = await connector.restAdapter.get(psUrl, { bearerToken: token });
    } catch(e) { console.log('Error fetching semesters:', e.message); process.exit(1); }

    const psList = psData?.prodiSemesters || psData?.data || [];
    
    console.log(`[2] Ditemukan ${psList.length} semester prodi aktif se-Fakultas.`);
    if (psList.length === 0) {
         console.log(JSON.stringify(psData).substring(0, 500));
         process.exit(1);
    }
    
    // Cleanup old PA accounts completely to start fresh for entire faculty
    const client = await db.pool.connect();
    await client.query("DELETE FROM users WHERE role = 'ADVISOR' AND username LIKE 'PA_%'");
    const hashed = '$2b$12$FCMiEQZ3wTWHR8oa47TE4ODtJUoiI/Tger84vjJsS6GAbAa/m5bVS'; 
    client.release();

    let totalDosen = 0;
    let totalMhs = 0;
    
    // Sort descending
    psList.sort((a,b) => (b.id_prodi_semester || 0) - (a.id_prodi_semester || 0));

    for (let i = 0; i < psList.length; i++) {
        const ps = psList[i];
        const idSem = ps.id || ps.id_prodi_semester;
        if (!idSem) continue;
        
        const prodiName = ps.prodi?.nama_resmi || ps.prodi?.nama || "Fakultas Ilmu Budaya";

        console.log(`[Progress ${i+1}/${psList.length}] Scraping Sem: ${idSem} (${prodiName})`);

        await new Promise(r => setTimeout(r, 1200));

        let data = null;
        try {
            data = await connector.restAdapter.get(`${BASE_URL}/api/admin/penasihat_akademik?filters[id_prodi_semester]=${idSem}`, { bearerToken: token });
        } catch(e) {
            console.warn(`[WARNING] Failed fetching Sem ${idSem}: ${e.message}`);
            continue;
        }

        if (!data) continue;

        let paArray = data.dosens || data.penasihat_akademiks || data.penasihatAkademiks || data.data || [];
        if (!Array.isArray(paArray)) paArray = [];
        
        for (const paObj of paArray) {
            const d = paObj.dosen || paObj;
            const nip = (d.nip || d.id_pegawai || d.username)?.toString();
            const nama = d.nama_dosen || d.nama || d.nama_pegawai;
            
            if (!nip) continue;
            
            const advId = await db.upsertAdvisor(nip, nama);
            await db.pool.query("UPDATE users SET hashed_password = $1 WHERE username = $2", [hashed, nip]);
            totalDosen++;

            const mahasiswas = paObj.mahasiswas || paObj.mahasiswa || paObj.bimbingan || [];
            const iterMhs = Array.isArray(mahasiswas) ? mahasiswas : [mahasiswas];
            for (const m of iterMhs) {
                const nim = (typeof m === 'string' ? m : (m.nim || m.id))?.toString();
                if (nim) {
                    try { 
                        const studName = m.nama_mahasiswa || m.nama || nim;
                        const defaultAngkatan = 2000 + parseInt(nim.substring(4, 6) || "20");
                        
                        await db.upsertStudent(nim, studName, isNaN(defaultAngkatan) ? 2020 : defaultAngkatan, prodiName, 'Aktif');
                        
                        await db.assignAdvisor(nim, advId); 
                        totalMhs++; 
                    } catch(e) {
                         // silently ignore
                    } 
                }
            }
        }
    }
    
    console.log(`\n============== SYNC PA SE-FAKULTAS SELESAI ==============`);
    console.log(`Total Dosen PA unik diperbarui: ${totalDosen}`);
    console.log(`Total Relasi Mahasiswa berhasil diikat: ${totalMhs}`);
    process.exit(0);
}
run();
