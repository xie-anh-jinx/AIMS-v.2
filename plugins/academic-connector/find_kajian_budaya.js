/**
 * find_kajian_budaya.js (v3)
 * 
 * Strategi yang sama dengan dump_all_pas.js:
 * - Login dengan akun yang ada
 * - Panggil prodi_semester?filters[is_used]=1 (TANPA filter id_prodi)
 * - API otomatis kembalikan semester dari prodi akun tersebut
 * - Kumpulkan semua data PA per semester
 * 
 * Lalu filter hanya PA dengan NIM mahasiswa prefix F062 atau prodi Kajian Budaya.
 */
import * as dotenv from 'dotenv';
dotenv.config({ path: '../.env' });
dotenv.config({ path: '.env' });

import fs from 'fs';
import YAML from 'yaml';
import { AcademicConnector } from './src/AcademicConnector.js';

const configRaw = fs.readFileSync('./config.yml', 'utf8');
const cfgBase   = YAML.parse(configRaw);
cfgBase.accounts = cfgBase.accounts.map(acc => {
  acc.username = acc.username.replace(/\${(.*?)}/g, (_, v) => process.env[v] || acc.username);
  acc.password = acc.password.replace(/\${(.*?)}/g, (_, v) => process.env[v] || acc.password);
  return acc;
});

// All 5 working accounts
const TARGET_ACCOUNTS = [
  'fib_sas_jepang',
  'fib_sas_prancis',
  'fib_pariwisata',
  'fib_sas_daerah',
  'fib_ilmu_sejarah',
];

const FIB_KEYWORDS = ['sastra', 'bahasa', 'linguistik', 'sejarah', 'arkeologi', 'pariwisata', 'budaya'];

function isFIB(nama) {
  if (!nama) return false;
  return FIB_KEYWORDS.some(kw => nama.toLowerCase().includes(kw));
}

async function main() {
  const connector = new AcademicConnector();

  const allProdiSemesters = {}; // id_prodi_semester → prodi_name
  const allPAByProdi      = {}; // prodi_name → [pa records]

  for (const accId of TARGET_ACCOUNTS) {
    const account = cfgBase.accounts.find(a => a.id === accId);
    if (!account) { console.warn(`⚠️  Account ${accId} not found in config`); continue; }

    console.log(`\n=============================`);
    console.log(`🔐 Login: ${account.program_studi}`);

    let tokens;
    try {
      tokens = await connector.browserAdapter.captureSessionToken(account);
    } catch (e) {
      console.error(`❌ Login failed: ${e.message}`);
      continue;
    }
    if (!tokens?.bearerToken) { console.error('❌ No token'); continue; }
    console.log('✅ Token acquired');

    const tok = tokens.bearerToken;

    // Get all prodi_semester for this account (no id_prodi filter)
    const psRes = await fetch(
      'https://api.neosia.unhas.ac.id/api/admin/prodi_semester?filters[is_used]=1',
      { headers: { Authorization: `Bearer ${tok}`, Accept: 'application/json' } }
    );
    const psJson  = await psRes.json();
    const psArr   = psJson.prodiSemesters ?? psJson.data ?? psJson ?? [];
    const semesters = Array.isArray(psArr) ? psArr : [];

    console.log(`📅 Found ${semesters.length} active semesters`);

    if (semesters.length === 0) continue;

    // Show what prodi this account controls
    const prodiNames = [...new Set(semesters.map(s =>
      s.prodi?.nama_resmi ?? s.prodi?.nama ?? `id_prodi_${s.id_prodi}`
    ))];
    console.log(`   Prodi covered: ${prodiNames.join(', ')}`);

    // Scrape penasihat_akademik for each semester
    let paForThisAccount = [];
    for (const ps of semesters) {
      const idSem = ps.id ?? ps.id_prodi_semester;
      if (!idSem) continue;

      await new Promise(r => setTimeout(r, 2000)); // Rate limit

      const paRes = await fetch(
        `https://api.neosia.unhas.ac.id/api/admin/penasihat_akademik?filters[id_prodi_semester]=${idSem}`,
        { headers: { Authorization: `Bearer ${tok}`, Accept: 'application/json' } }
      );
      if (!paRes.ok) continue;

      const paJson = await paRes.json();
      const paArr  = paJson.dosens ?? paJson.penasihat_akademiks ?? paJson.data ?? paJson ?? [];
      const entries = Array.isArray(paArr) ? paArr : [];

      if (entries.length > 0) {
        paForThisAccount.push(...entries);
        process.stdout.write(`[${entries.length}]`);
      } else {
        process.stdout.write('.');
      }
    }

    console.log(`\n✅ ${paForThisAccount.length} PA entries collected for ${account.program_studi}`);

    // Segregate by prodi name
    for (const entry of paForThisAccount) {
      const prodiName = entry?.dosen?.prodi?.nama_resmi
        ?? entry?.prodi?.nama_resmi
        ?? semesters[0]?.prodi?.nama_resmi
        ?? account.program_studi;

      if (!allPAByProdi[prodiName]) allPAByProdi[prodiName] = [];
      allPAByProdi[prodiName].push(entry);
    }
  }

  // ── Report all unique prodi found ──────────────────────────────────────────
  console.log('\n\n══════════════════════════════════════════');
  console.log('📋 SEMUA PRODI YANG DITEMUKAN:');

  for (const [prodi, entries] of Object.entries(allPAByProdi)) {
    const isFib = isFIB(prodi);
    console.log(`  ${isFib ? '✅' : '⬡ '} ${prodi}: ${entries.length} PA records`);

    // Sample NIM mahasiswa
    const nims = new Set();
    for (const e of entries) {
      for (const mh of (e.mahasiswas ?? [])) {
        nims.add(mh.nim ?? '?');
      }
    }
    const nimSample = [...nims].slice(0, 3).join(', ');
    if (nimSample) console.log(`     Sample NIM: ${nimSample}...`);
  }

  // Filter untuk Kajian Budaya / F062
  const kajianBudayaData = Object.entries(allPAByProdi)
    .filter(([prodi]) => prodi.toLowerCase().includes('budaya') || prodi.toLowerCase().includes('kajian'))
    .flatMap(([, entries]) => entries);

  console.log(`\n🔎 Kajian Budaya data: ${kajianBudayaData.length} PA records`);

  // Save full dump for further processing
  fs.writeFileSync(
    './kajian_budaya_pa.json',
    JSON.stringify({ byProdi: allPAByProdi, kajianBudaya: kajianBudayaData }, null, 2)
  );
  console.log('💾 Saved to kajian_budaya_pa.json');
  process.exit(0);
}

main().catch(e => { console.error(e); process.exit(1); });
