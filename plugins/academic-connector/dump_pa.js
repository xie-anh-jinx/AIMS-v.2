/**
 * Direct PA Payload Dumper - gunakan token dari session yang sudah ada
 * Tidak membutuhkan login browser baru
 */
import fs from 'fs';
import { SessionManager } from './src/core/SessionManager.js';
import { RestAdapter } from './src/adapters/RestAdapter.js';

const BASE_URL = 'https://api.neosia.unhas.ac.id';
const logger = { 
    info: (...a) => console.log('[INFO]', ...a), 
    warn: (...a) => console.warn('[WARN]', ...a), 
    error: (...a) => console.error('[ERROR]', ...a), 
    debug: () => {} 
};

const rest = new RestAdapter({ maxRetries: 1 }, logger);
const session = new SessionManager(rest, logger);
await session.initialize();

// Ambil semua session yang tersedia
const accounts = ['fib_pariwisata', 'fib_sas_prancis', 'fib_sas_jepang', 'fib_sas_daerah', 'fib_ilmu_sejarah'];

let activeToken = null;
let activeAccount = null;
for (const acc of accounts) {
    const s = session._sessions?.get(acc) || session._sessions?.[acc];
    // Try load from file
    const sessionFile = `./providers/${acc}/session.json`;
    if (fs.existsSync(sessionFile)) {
        try {
            const data = JSON.parse(fs.readFileSync(sessionFile, 'utf8'));
            if (data.bearerToken) {
                activeToken = data.bearerToken;
                activeAccount = acc;
                console.log(`[OK] Loaded token from ${acc}`);
                break;
            }
        } catch(e) {}
    }
}

if (!activeToken) {
    console.log("Tidak ada token tersimpan. Jalankan example.js dulu.");
    process.exit(1);
}

const headers = { 
    Authorization: `Bearer ${activeToken}`,
    Accept: 'application/json'
};

console.log(`\nUsing account: ${activeAccount}`);
console.log("=".repeat(60));

// Step 1: Ambil semua prodi_semester aktif
console.log("\n[1] Fetching prodi_semester aktif...");
const ps_res = await fetch(`${BASE_URL}/api/admin/prodi_semester?filters[is_used]=1`, { headers });
const ps_json = await ps_res.json();
const ps_keys = Object.keys(ps_json);
console.log("prodi_semester root keys:", ps_keys);

const ps_arr = ps_json.prodiSemesters || ps_json.data || ps_json.items || ps_json[ps_keys[0]];
console.log("Array length:", Array.isArray(ps_arr) ? ps_arr.length : 'NOT ARRAY');
if (Array.isArray(ps_arr) && ps_arr.length > 0) {
    console.log("Sample prodi_semester[0] keys:", Object.keys(ps_arr[0]).join(', '));
    console.log("Sample prodi_semester[0]:", JSON.stringify(ps_arr[0], null, 2));
}

// Step 2: Ambil PA untuk beberapa id_prodi_semester pertama
if (Array.isArray(ps_arr) && ps_arr.length > 0) {
    const testIds = ps_arr.slice(0, 3).map(p => p.id || p.id_prodi_semester);
    
    for (const idSem of testIds) {
        console.log(`\n[2] Fetching PA for id_prodi_semester=${idSem}...`);
        const pa_res = await fetch(`${BASE_URL}/api/admin/penasihat_akademik?filters[id_prodi_semester]=${idSem}`, { headers });
        const pa_json = await pa_res.json();
        
        const pa_keys = Object.keys(pa_json);
        console.log("PA root keys:", pa_keys);
        const pa_arr = pa_json.penasihat_akademiks || pa_json.penasihatAkademiks || pa_json.data || pa_json[pa_keys[0]];
        console.log("PA Array length:", Array.isArray(pa_arr) ? pa_arr.length : typeof pa_arr);
        if (Array.isArray(pa_arr) && pa_arr.length > 0) {
            console.log("Sample PA[0] ALL KEYS:", Object.keys(pa_arr[0]).join(', '));
            console.log("Sample PA[0]:", JSON.stringify(pa_arr[0], null, 2));
            break; // Cukup satu sample
        }
    }
}
