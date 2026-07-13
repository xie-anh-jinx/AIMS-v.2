import fs from 'fs';
import YAML from 'yaml';
import dotenv from 'dotenv';
import { AcademicConnector } from './src/AcademicConnector.js';

dotenv.config({ path: '../../.env' });

const configRaw = fs.readFileSync('./config.yml', 'utf8');
const config = YAML.parse(configRaw);

async function run() {
    const connector = new AcademicConnector();
    connector.restAdapter.baseUrl = 'https://api.neosia.unhas.ac.id';
    
    const account = config.accounts.find(a => a.id === "fib_superadmin");
    console.log(`Logging in via Playwright as Fakultas Super Admin...`);
    
    // 1. Capture token via UI Login
    const tokens = await connector.browserAdapter.captureSessionToken(account);
    if (!tokens || !tokens.bearerToken) {
        console.error(`Gagal autentikasi untuk Fakultas Ilmu Budaya.`);
        process.exit(1);
    }
    console.log(`Berhasil login Fakultas! Token Date: ${tokens.timestamp}`);
    
    // 2. Fetch Prodi Semester list
    const psUrl = 'https://api.neosia.unhas.ac.id/api/admin/prodi_semester?filters[is_used]=1';
    const psData = await connector.restAdapter.get(psUrl, { bearerToken: tokens.bearerToken });
    const psArr = psData.prodiSemesters || psData.data || [];
    console.log(`Ditemukan ${psArr.length} semester prodi aktif di seluruh fakultas.`);
    
    let paDataAll = [];
    let fetchCount = 0;
    
    for (const ps of psArr) {
        const idSem = ps.id || ps.id_prodi_semester;
        const prodiName = ps.prodi?.nama_resmi || ps.prodi?.nama || "Unknown Prodi";
        if (!idSem) continue;
        
        await new Promise(r => setTimeout(r, 1000)); // anti-spam
        const paUrl = `https://api.neosia.unhas.ac.id/api/admin/penasihat_akademik?filters[id_prodi_semester]=${idSem}`;
        const paData = await connector.restAdapter.get(paUrl, { bearerToken: tokens.bearerToken });
        let paArr = paData.dosens || paData.penasihat_akademiks || paData.data || [];
        if (!Array.isArray(paArr)) paArr = paArr.data || [];
        
        console.log(`- Extracted ${paArr.length} PAs from [${prodiName}] for Sem ${ps.semester?.nama || idSem}`);
        paDataAll.push(...paArr);
        fetchCount++;
    }
    
    fs.writeFileSync('pa_dump_fib_all.json', JSON.stringify(paDataAll, null, 2));
    console.log(`\nSelesai! Menyimpan total ${paDataAll.length} data record PA Se-Fakultas ke pa_dump_fib_all.json`);
    process.exit(0);
}
run();
