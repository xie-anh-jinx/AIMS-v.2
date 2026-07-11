/**
 * scan_prodi_fib.js  (v2)
 * 
 * Strategy: Login with EACH prodi account we have, then call
 * /api/admin/dosen?filters[id_prodi]=<THEIR_ID> for their own prodi.
 * Additionally, probe unknown prodi IDs 30-40 using any working token
 * via /api/admin/prodi endpoint to identify what those prodi IDs are.
 */
import * as dotenv from 'dotenv';
dotenv.config({ path: '../.env' });
dotenv.config({ path: '.env' });

import { chromium } from 'playwright';
import fs from 'fs';

const API_BASE = 'https://api.neosia.unhas.ac.id';
const PORTAL = 'https://backoffice.neosia.unhas.ac.id/login';

const FIB_KEYWORDS = [
  'sastra', 'bahasa', 'linguistik', 'sejarah', 'arkeologi',
  'pariwisata', 'budaya', 'ilmu budaya'
];

function isFIB(nama) {
  if (!nama) return false;
  return FIB_KEYWORDS.some(kw => nama.toLowerCase().includes(kw));
}

// All available accounts
const ACCOUNTS = [
  { label: 'Sastra Jepang',  user: process.env.ENV_PRODI_JEP_USER, pass: process.env.ENV_PRODI_JEP_PASS },
  { label: 'Sastra Prancis', user: process.env.ENV_PRODI_FRA_USER, pass: process.env.ENV_PRODI_FRA_PASS },
  { label: 'Pariwisata',     user: process.env.ENV_PRODI_PAR_USER, pass: process.env.ENV_PRODI_PAR_PASS },
  { label: 'Sastra Daerah',  user: process.env.ENV_PRODI_DAE_USER, pass: process.env.ENV_PRODI_DAE_PASS },
  { label: 'Ilmu Sejarah',   user: process.env.ENV_PRODI_SEJ_USER, pass: process.env.ENV_PRODI_SEJ_PASS },
];

async function loginAndGetToken(account) {
  console.log(`\n🔐 Logging in: ${account.label}...`);
  let capturedToken = null;

  const browser = await chromium.launch({ headless: true, slowMo: 80 });
  const ctx  = await browser.newContext();
  const page = await ctx.newPage();

  page.on('request', req => {
    const auth = req.headers()['authorization'];
    if (auth && auth.startsWith('Bearer ') && !capturedToken) {
      capturedToken = auth.replace('Bearer ', '');
    }
  });

  await page.goto(PORTAL, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await page.fill('input[type="text"], input[name="username"], #userId', account.user);
  await page.fill('input[type="password"]', account.pass);
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle', timeout: 90000 }).catch(() => {}),
    page.click('button[type="submit"], input[type="submit"], .btn-login')
  ]);
  await page.waitForTimeout(4000);

  // Navigate a bit to trigger API calls
  try {
    await page.goto('https://backoffice.neosia.unhas.ac.id/dashboard', { timeout: 20000 }).catch(() => {});
    await page.waitForTimeout(3000);
  } catch (_) {}

  await browser.close();

  if (capturedToken) {
    console.log(`  ✅ Token captured for ${account.label}`);
  } else {
    console.log(`  ❌ No token captured for ${account.label}`);
  }
  return capturedToken;
}

async function apiGet(url, token) {
  const res = await fetch(url, {
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/json' }
  });
  if (!res.ok) return null;
  return res.json();
}

async function main() {
  const fibResult = {};

  // --- Step 1: For each account, find out what prodi they control
  //             and get dosen for that prodi ---
  for (const account of ACCOUNTS) {
    const token = await loginAndGetToken(account);
    if (!token) continue;

    // Probe prodi IDs 30-40 with this token
    for (let id_prodi = 30; id_prodi <= 40; id_prodi++) {
      if (fibResult[id_prodi]) continue; // already found
      await new Promise(r => setTimeout(r, 1000)); // rate limit

      const dosenData = await apiGet(
        `${API_BASE}/api/admin/dosen?filters[id_prodi]=${id_prodi}`,
        token
      );

      if (!dosenData) {
        process.stdout.write('.');
        continue;
      }

      const dosenArr = Array.isArray(dosenData) ? dosenData : (dosenData?.data ?? []);
      if (!dosenArr.length) continue;

      // Get prodi name
      const sampleDosen = dosenArr[0];
      const namaProdi =
        sampleDosen?.prodi?.nama_resmi ||
        sampleDosen?.prodi?.nama ||
        sampleDosen?.prodi?.kode_dikti ||
        `id_prodi_${id_prodi}`;

      console.log(`\n  📚 id_prodi=${id_prodi}: ${namaProdi} (${dosenArr.length} dosen)`);

      if (!isFIB(namaProdi)) {
        console.log(`     🚫 NOT FIB — skipped.`);
        continue;
      }

      console.log(`     ✅ FIB! Saving ${dosenArr.length} dosen...`);
      fibResult[id_prodi] = {
        namaProdi,
        loginAccount: account.label,
        dosenCount: dosenArr.length,
        dosen: dosenArr.map(d => ({
          nip:    d.nip  ?? d.nidn ?? null,
          nidn:   d.nidn ?? null,
          nama:   d.nama ?? 'N/A',
          is_active: d.is_active,
        }))
      };
    }
  }

  // --- Step 2: Report ---
  console.log('\n\n========================================');
  console.log('📋 HASIL SCAN FIB PA (id_prodi 30-40):');
  console.log('========================================');

  if (!Object.keys(fibResult).length) {
    console.log('⚠️  Tidak ada prodi FIB yang ditemukan di rentang 30-40 dengan akun yang tersedia.');
    console.log('   Kemungkinan prodi tersebut menggunakan akun berbeda.');
  }

  for (const [id_prodi, prodi] of Object.entries(fibResult)) {
    console.log(`\n🏫 [id_prodi=${id_prodi}] ${prodi.namaProdi} — ${prodi.dosenCount} Dosen (via akun "${prodi.loginAccount}")`);
    for (const d of prodi.dosen) {
      console.log(`   • ${String(d.nama).padEnd(50)} NIP: ${d.nip ?? 'N/A'}`);
    }
  }

  fs.writeFileSync('./fib_prodi_scan.json', JSON.stringify(fibResult, null, 2));
  console.log('\n💾 Saved to plugins/academic-connector/fib_prodi_scan.json');
}

main().catch(console.error);
