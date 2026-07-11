import fs from 'fs';
import YAML from 'yaml';
import { AcademicConnector } from './src/AcademicConnector.js';

const config = YAML.parse(fs.readFileSync('./config.yml', 'utf8'));

async function fastFixPA() {
    console.log("=== MEMULAI SINKRONISASI PA EXPRESS ===");
    const connector = new AcademicConnector();
    
    const accounts = config.accounts;
    let session = null;
    let loggedInAccount = null;

    for (const acc of accounts) {
        try {
            console.log(`[Browser] Mencoba Login untuk ${acc.id}...`);
            session = await connector.browserAdapter.captureSessionToken(acc);
            console.log(`[Auth] Token Intercepted Successfully for ${acc.id}.`);
            loggedInAccount = acc;
            break; // Sukses, keluar dari loop
        } catch(err) {
            console.log(`[WARN] Gagal login ${acc.id}, mencoba akun lain... (${err.message})`);
        }
    }

    if (!session) throw new Error("Gagal login ke semua akun terdaftar!");

    connector.sessionManager.pool.set(loggedInAccount.id, {
        bearerToken: session.bearerToken,
        cookies: session.cookies,
        timestamp: Date.now()
    });
    // Build the Client manually
    const { NeoSIAClient } = await import('./src/clients/NeoSIAClient.js');
    const providerPath = `./providers/${loggedInAccount.provider || 'neosia'}`;
    const client = new NeoSIAClient(connector.restAdapter, connector.sessionManager, loggedInAccount, providerPath, connector.logger);
    
    console.log("[API] Mengambil daftar prodi_semester...");
    const psRes = await client.rest.get(`${client.baseUrl}/api/admin/prodi_semester?filters[is_used]=1`, client._getSession());
    
    let psList = [];
    if (psRes && !Array.isArray(psRes)) {
        psList = psRes.prodiSemesters || psRes.data || psRes.items || [];
    } else {
        psList = psRes;
    }
    
    console.log(`[API] Ditemukan ${psList.length} semester aktif. Mulai mapping PA...`);
    
    // Purge fake PA
    await connector.dbAdapter.pool.query("DELETE FROM users WHERE role = 'ADVISOR' AND username LIKE 'PA_%'");
    const hashed = '$2b$12$FCMiEQZ3wTWHR8oa47TE4ODtJUoiI/Tger84vjJsS6GAbAa/m5bVS'; // password123

    let advisorMap = {};
    let totalDosen = 0;

    for (const ps of psList) {
        const idSem = ps.id || ps.id_prodi_semester;
        if (!idSem) continue;

        try {
            const paRes = await client.getPenasihatAkademik(idSem);
            let paArray = paRes;
            if (paRes && typeof paRes === 'object' && !Array.isArray(paRes)) {
                paArray = paRes.dosens || paRes.penasihat_akademiks || paRes.penasihatAkademiks || paRes.data || [];
            }
            if (!Array.isArray(paArray)) continue;

            for (const paObj of paArray) {
                const pa = paObj.dosen || paObj;
                const nip = (pa.nip || pa.id_pegawai || pa.username)?.toString();
                if (!nip) continue;

                const nama = pa.nama_dosen || pa.nama || pa.nama_pegawai || ("Dosen " + nip);
                const advId = await connector.dbAdapter.upsertAdvisor(nip, nama);
                await connector.dbAdapter.pool.query("UPDATE users SET hashed_password = $1 WHERE username = $2", [hashed, nip]);
                
                totalDosen++;

                const mhsList = paObj.mahasiswas || paObj.mahasiswa || paObj.mahasiswa_bimbingan || paObj.bimbingan || [];
                for (const mhs of (Array.isArray(mhsList) ? mhsList : [mhsList])) {
                    const nimStr = (typeof mhs === 'string' ? mhs : (mhs.nim || mhs.id))?.toString();
                    if (nimStr) advisorMap[nimStr] = advId;
                }
            }
        } catch(err) {
            // Ignore API timeout 403 on single sem
        }
    }
    
    console.log(`[Mapping] Berhasil menemukan ${totalDosen} profil PA.`);
    console.log(`[Mapping] Ditemukan ${Object.keys(advisorMap).length} relasi mahasiswa-dosen. Memasukkan ke DB...`);

    let linked = 0;
    for (const [nim, advId] of Object.entries(advisorMap)) {
        try {
            await connector.dbAdapter.assignAdvisor(nim, advId);
            linked++;
        } catch(err) {
            // Student belum tersinkron di DB
        }
    }

    console.log(`[DONE] ${linked} mahasiswa berhasil diikat!`);
    console.log(`[INFO] Semua NIP PA (${totalDosen}) kini bisa login dengan password: password123`);
    process.exit(0);
}

fastFixPA();
