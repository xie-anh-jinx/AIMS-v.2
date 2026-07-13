/**
 * login_and_fetch_all.js
 * ──────────────────────
 * Login ulang ke Neosia menggunakan kredensial FIB Superadmin,
 * lalu fetch seluruh data PA + Mahasiswa se-Fakultas.
 * Simpan hasilnya sebagai pa_dump_all_v2.json
 *
 * Jalankan: cd plugins/academic-connector && node login_and_fetch_all.js
 */

import fs from 'fs';
import path from 'path';

const BASE_URL   = 'https://neosia.unhas.ac.id';
const API_URL    = 'https://api.neosia.unhas.ac.id';
const OUT_FILE   = path.resolve('./pa_dump_all_v2.json');

// Kredensial FIB Superadmin (Arkeologi sudah terbukti bisa akses se-Fakultas)
const CREDS = { username: 'F_7371125410970003', password: '28141' };

async function login() {
    console.log('[AUTH] Login ke Neosia…');
    const res = await fetch(`${BASE_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(CREDS),
        redirect: 'manual',
    });
    // Coba endpoint API langsung
    const res2 = await fetch(`${API_URL}/oauth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ username: CREDS.username, password: CREDS.password, grant_type: 'password' }),
    });
    if (res2.ok) {
        const d = await res2.json();
        const token = d.access_token ?? d.token ?? d.bearerToken;
        if (token) { console.log('[AUTH] Bearer token diperoleh via OAuth ✓'); return token; }
    }
    // Coba cara lain - session cookie
    const html = await res.text().catch(() => '');
    const tokenMatch = html.match(/"token"\s*:\s*"([^"]+)"/);
    if (tokenMatch) { console.log('[AUTH] Token dari HTML ✓'); return tokenMatch[1]; }
    
    // Ambil dari cookie XSRF
    const setCookies = res.headers.get('set-cookie') ?? '';
    const xsrfMatch  = setCookies.match(/XSRF-TOKEN=([^;]+)/);
    const sessMatch  = setCookies.match(/neosia_session=([^;]+)/);
    if (xsrfMatch && sessMatch) {
        return { type: 'cookie', xsrf: decodeURIComponent(xsrfMatch[1]), session: sessMatch[1] };
    }

    throw new Error(`Login gagal. Status: ${res.status}`);
}

async function apiGet(path, authHeader) {
    const url = `${API_URL}${path}`;
    const res = await fetch(url, { headers: { ...authHeader, 'Accept': 'application/json' } });
    if (!res.ok) throw new Error(`${res.status} ${res.statusText} → ${url}`);
    return res.json();
}

async function discoverEndpoints(authHeader) {
    // Coba berbagai endpoint untuk daftar semester
    const tries = [
        '/api/semester',
        '/api/akademik/semester',
        '/api/master/semester',
        '/api/v1/semester',
    ];
    for (const ep of tries) {
        try {
            const r = await apiGet(ep, authHeader);
            const arr = r.data ?? r;
            if (Array.isArray(arr) && arr.length > 0) {
                console.log(`[INFO] Semester endpoint: ${ep}`);
                return { semEp: ep, semesters: arr.sort((a,b) => b.id - a.id).slice(0, 5) };
            }
        } catch(_) {}
    }
    // Fallback: gunakan ID yang diketahui
    return { semEp: null, semesters: [{ id: 4036 }, { id: 4035 }, { id: 4034 }, { id: 4033 }] };
}

async function fetchPaForSemester(semId, authHeader) {
    // Coba berbagai endpoint PA
    const tries = [
        `/api/penasihat-akademik?id_semester=${semId}&per_page=999`,
        `/api/penasihat_akademik?id_semester=${semId}&perPage=999`,
        `/api/pa?id_semester=${semId}&limit=999`,
        `/api/dosen/pa?semester_id=${semId}`,
        `/api/akademik/penasihat-akademik?semester=${semId}`,
    ];
    for (const ep of tries) {
        try {
            const r   = await apiGet(ep, authHeader);
            let   arr = r;
            if (r && typeof r === 'object' && !Array.isArray(r)) {
                arr = r.data ?? r.penasihat_akademiks ?? r.penasihatAkademiks 
                    ?? r.items ?? r.list ?? r.dosen
                    ?? Object.values(r).find(v => Array.isArray(v)) ?? [];
            }
            if (Array.isArray(arr) && arr.length > 0) {
                console.log(`  [${semId}] Endpoint: ${ep} → ${arr.length} PA`);
                return arr;
            }
        } catch(_) {}
    }
    return [];
}

async function main() {
    // 1. Login
    let token, authHeader;
    try {
        token = await login();
        if (typeof token === 'string') {
            authHeader = { 'Authorization': `Bearer ${token}` };
        } else if (token?.type === 'cookie') {
            authHeader = {
                'Cookie': `XSRF-TOKEN=${token.xsrf}; neosia_session=${token.session}`,
                'X-XSRF-TOKEN': token.xsrf,
            };
        }
    } catch(e) {
        console.error('[FATAL] Login gagal:', e.message);
        process.exit(1);
    }

    // 2. Discover semester endpoint
    const { semesters } = await discoverEndpoints(authHeader);
    console.log(`[INFO] Akan fetch ${semesters.length} semester: ${semesters.map(s => s.id).join(', ')}`);

    // 3. Fetch PA untuk setiap semester
    const allPaRecords = [];
    const seenId       = new Map();

    for (const sem of semesters) {
        const semId  = sem.id;
        console.log(`\n[SEM ${semId}] Fetching…`);
        const paList = await fetchPaForSemester(semId, authHeader);
        console.log(`  → ${paList.length} PA ditemukan`);
        
        for (const paObj of paList) {
            const dosen     = paObj.dosen ?? paObj;
            const key       = String(dosen.id ?? dosen.nip ?? dosen.nidn ?? '');
            const mahasiswas = paObj.mahasiswas ?? paObj.bimbingan ?? [];
            
            if (!key) continue;
            
            if (seenId.has(key)) {
                const rec       = allPaRecords[seenId.get(key)];
                const existNims = new Set(rec.mahasiswas.map(m => typeof m === 'string' ? m : m?.nim));
                for (const mhs of mahasiswas) {
                    const nim = typeof mhs === 'string' ? mhs : mhs?.nim;
                    if (nim && !existNims.has(nim)) { rec.mahasiswas.push(mhs); existNims.add(nim); }
                }
            } else {
                seenId.set(key, allPaRecords.length);
                allPaRecords.push({ dosen, mahasiswas: [...mahasiswas] });
            }
        }
    }

    const totalNim = new Set(
        allPaRecords.flatMap(r => r.mahasiswas.map(m => typeof m === 'string' ? m : m?.nim))
    ).size;

    console.log(`\n[INFO] Total PA unik    : ${allPaRecords.length}`);
    console.log(`[INFO] Total mahasiswa   : ${totalNim}`);

    // 4. Simpan
    fs.writeFileSync(OUT_FILE, JSON.stringify(allPaRecords, null, 0), 'utf8');
    console.log(`[SAVE] Tersimpan ke ${OUT_FILE}`);
    console.log('\n[DONE] Sekarang jalankan: python3 sync_neosia_to_db.py');
}

main().catch(e => { console.error('[FATAL]', e.message); process.exit(1); });
