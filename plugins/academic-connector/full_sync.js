/**
 * full_sync.js — Sinkronisasi penuh FIB Neosia → AIMS
 * ──────────────────────────────────────────────────────
 * Login ke backoffice Neosia (React SPA) via Playwright,
 * capture Bearer token, fetch semua PA + mahasiswas se-FIB,
 * simpan ke pa_dump_all_full.json
 *
 * cd plugins/academic-connector && node full_sync.js
 */

import fs from 'fs';
import path from 'path';
import { chromium } from 'playwright';

const API_BASE  = 'https://api.neosia.unhas.ac.id';
const LOGIN_URL = 'https://backoffice.neosia.unhas.ac.id/login';
const CREDS     = { username: 'F_7371125410970003', password: '28141' };
const OUT_PATH  = path.resolve('./pa_dump_all_full.json');
const SES_DIR   = path.resolve('./providers/fib_superadmin');

async function captureToken() {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page    = await context.newPage();

    let bearerToken = null;

    // Intercept API requests untuk capture Authorization header
    page.on('request', (req) => {
        const auth = req.headers()['authorization'];
        if (auth?.startsWith('Bearer ') && !bearerToken) {
            bearerToken = auth.replace('Bearer ', '');
            console.log('[AUTH] Token captured from request intercept ✓');
        }
    });

    page.on('response', async (res) => {
        try {
            const url = res.url();
            // Coba parse response yang mengandung token
            if (!bearerToken && url.includes('/auth') && res.status() === 200) {
                const body = await res.text().catch(() => '');
                const m    = body.match(/"(?:access_token|token|bearerToken)"\s*:\s*"([A-Za-z0-9._-]{50,})"/);
                if (m) { bearerToken = m[1]; console.log('[AUTH] Token dari response body ✓'); }
            }
        } catch(_) {}
    });

    console.log('[AUTH] Navigasi ke halaman login (React SPA)…');
    try {
        await page.goto(LOGIN_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
    } catch(e) {
        console.log('[WARN] Timeout tapi lanjut:', e.message.split('\n')[0]);
    }

    // Tunggu React render form — coba berbagai selector
    const inputSelectors = [
        'input[type="text"]',
        'input[id*="user" i]',
        'input[placeholder*="user" i]',
        'input[placeholder*="nim" i]',
        'input[name*="user" i]',
        '#username',
        '[data-testid*="user" i]',
    ];

    let usernameEl = null;
    console.log('[AUTH] Menunggu form login muncul…');
    for (let attempt = 0; attempt < 20; attempt++) {
        await page.waitForTimeout(1000);
        for (const sel of inputSelectors) {
            try {
                const el = page.locator(sel).first();
                const cnt = await el.count();
                if (cnt > 0) {
                    usernameEl = sel;
                    console.log(`[AUTH] Form ditemukan: ${sel}`);
                    break;
                }
            } catch(_) {}
        }
        if (usernameEl) break;
    }

    if (!usernameEl) {
        // Screenshot untuk debug
        await page.screenshot({ path: 'login_debug.png' });
        console.log('[WARN] Form tidak ditemukan, screenshot disimpan ke login_debug.png');
        // Coba ambil semua input yang ada
        const inputs = await page.$$('input');
        console.log(`[DEBUG] Total input di halaman: ${inputs.length}`);
        for (const inp of inputs) {
            const attrs = await inp.evaluate(el => ({
                type: el.type, name: el.name, id: el.id, placeholder: el.placeholder
            }));
            console.log('  Input:', JSON.stringify(attrs));
        }
        await browser.close();
        throw new Error('Form login tidak ditemukan setelah 20 detik');
    }

    // Isi form
    const passSelectors = ['input[type="password"]', 'input[id*="pass" i]', 'input[placeholder*="pass" i]'];
    let passwordEl = null;
    for (const sel of passSelectors) {
        try {
            const cnt = await page.locator(sel).count();
            if (cnt > 0) { passwordEl = sel; break; }
        } catch(_) {}
    }

    console.log(`[AUTH] Mengisi: ${usernameEl} dan ${passwordEl}`);
    await page.fill(usernameEl, CREDS.username);
    if (passwordEl) await page.fill(passwordEl, CREDS.password);

    // Submit
    const submitSels = ['button[type="submit"]', 'button:has-text("Login")', 'button:has-text("Masuk")', '[type="submit"]'];
    for (const sel of submitSels) {
        try {
            const cnt = await page.locator(sel).count();
            if (cnt > 0) { await page.click(sel); break; }
        } catch(_) {}
    }

    // Tunggu redirect & API call
    console.log('[AUTH] Menunggu login dan redirect…');
    await page.waitForTimeout(8000);

    // Coba trigger API call agar token muncul
    if (!bearerToken) {
        console.log('[AUTH] Memancing API call untuk capture token…');
        await page.evaluate(() => {
            // Trigger navigation / data load yang biasanya memanggil API
            window.dispatchEvent(new Event('popstate'));
        });
        await page.waitForTimeout(3000);
    }

    // Cek localStorage untuk token
    if (!bearerToken) {
        const token = await page.evaluate(() => {
            const keys = Object.keys(localStorage || {});
            for (const k of keys) {
                const v = localStorage.getItem(k) || '';
                if (v.length > 100) {
                    try {
                        const p = JSON.parse(v);
                        return p.token || p.access_token || p.bearerToken || null;
                    } catch(_) {}
                    if (v.match(/^eyJ/)) return v; // JWT
                }
            }
            return null;
        });
        if (token) { bearerToken = token; console.log('[AUTH] Token dari localStorage ✓'); }
    }

    // Cek sessionStorage
    if (!bearerToken) {
        const token = await page.evaluate(() => {
            const keys = Object.keys(sessionStorage || {});
            for (const k of keys) {
                const v = sessionStorage.getItem(k) || '';
                if (v.match(/^eyJ/)) return v;
            }
            return null;
        });
        if (token) { bearerToken = token; console.log('[AUTH] Token dari sessionStorage ✓'); }
    }

    await browser.close();
    return bearerToken;
}

async function apiFetch(path, headers) {
    const url = `${API_BASE}${path}`;
    const res = await fetch(url, { headers });
    if (!res.ok) throw new Error(`${res.status} → ${url}`);
    return res.json();
}

async function main() {
    // 1. Dapatkan token
    console.log('[STEP 1] Login dan capture Bearer token dari Neosia…');
    let token;
    try {
        token = await captureToken();
    } catch(e) {
        console.error('[FATAL]', e.message);
        process.exit(1);
    }

    if (!token) {
        console.error('[FATAL] Gagal mendapatkan Bearer token. Periksa koneksi internet atau kredensial.');
        process.exit(1);
    }

    // Simpan session
    fs.mkdirSync(SES_DIR, { recursive: true });
    fs.writeFileSync(path.join(SES_DIR, 'session.json'), JSON.stringify({ bearerToken: token }, null, 2));
    console.log(`[INFO] Session disimpan ✓`);

    const headers = {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/json',
    };

    // 2. Fetch semua prodi_semester aktif
    console.log('\n[STEP 2] Mengambil prodi_semester aktif se-FIB…');
    const psData = await apiFetch('/api/admin/prodi_semester?filters[is_used]=1&per_page=999', headers);
    const psArr  = psData.prodiSemesters ?? psData.data ?? [];
    console.log(`  → ${psArr.length} prodi_semester ditemukan`);

    if (psArr.length === 0) {
        console.error('[FATAL] Tidak ada prodi_semester. Cek token.');
        process.exit(1);
    }

    // 3. Fetch PA per prodi_semester
    console.log(`\n[STEP 3] Fetching PA + mahasiswas untuk ${psArr.length} prodi_semester…`);

    const allPaRecords = [];
    const seenKey      = new Map();

    for (let i = 0; i < psArr.length; i++) {
        const ps   = psArr[i];
        const idPs = ps.id ?? ps.id_prodi_semester;
        if (!idPs) continue;

        const nama = (ps.prodi?.nama_resmi ?? ps.nama ?? `PS-${idPs}`).substring(0,35);
        process.stdout.write(`\r  [${String(i+1).padStart(3)}/${psArr.length}] ${nama.padEnd(35)}`);

        try {
            const paData = await apiFetch(
                `/api/admin/penasihat_akademik?filters[id_prodi_semester]=${idPs}`,
                headers
            );
            const paList = paData.dosens ?? paData.penasihat_akademiks ?? 
                           paData.penasihatAkademiks ?? paData.data ?? paData.items ?? [];

            for (const paObj of paList) {
                const dosen      = paObj.dosen ?? paObj;
                const key        = String(dosen.id ?? dosen.nip ?? dosen.nidn ?? '');
                const mahasiswas = paObj.mahasiswas ?? paObj.bimbingan ?? [];

                if (!key) continue;

                if (seenKey.has(key)) {
                    const rec      = allPaRecords[seenKey.get(key)];
                    const existing = new Set(rec.mahasiswas.map(m => typeof m === 'string' ? m : m?.nim));
                    for (const mhs of mahasiswas) {
                        const nim = typeof mhs === 'string' ? mhs : mhs?.nim;
                        if (nim && !existing.has(nim)) { rec.mahasiswas.push(mhs); existing.add(nim); }
                    }
                } else {
                    seenKey.set(key, allPaRecords.length);
                    allPaRecords.push({ dosen, mahasiswas: [...mahasiswas] });
                }
            }
        } catch(e) {
            // Lanjut ke prodi_semester berikutnya
        }
    }

    const allNims = new Set(
        allPaRecords.flatMap(r => r.mahasiswas.map(m => typeof m === 'string' ? m : m?.nim).filter(Boolean))
    );

    console.log(`\n\n[RESULT] Total Dosen PA unik  : ${allPaRecords.length}`);
    console.log(`[RESULT] Total mahasiswa unik  : ${allNims.size}`);

    // 4. Simpan dump
    fs.writeFileSync(OUT_PATH, JSON.stringify(allPaRecords, null, 0), 'utf8');
    console.log(`[SAVE] Dump tersimpan: ${OUT_PATH} (${(fs.statSync(OUT_PATH).size / 1024 / 1024).toFixed(1)} MB)`);
    console.log('\n✅ Sekarang jalankan:');
    console.log('   python3 sync_neosia_to_db.py');
}

main().catch(e => { console.error('\n[FATAL]', e.message, e.stack?.split('\n')[1]); process.exit(1); });
