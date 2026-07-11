import fs from 'fs';
import YAML from 'yaml';
import dotenv from 'dotenv';
import { AcademicConnector } from './src/AcademicConnector.js';

dotenv.config({ path: './.env' }); // Load Env

const configRaw = fs.readFileSync('./config.yml', 'utf8');
const config = YAML.parse(configRaw);

// Manually interpolate config accounts
config.accounts = config.accounts.map(acc => {
    // Basic interpolation for ${VAR}
    acc.username = acc.username.replace(/\${(.*?)}/g, (_, v) => process.env[v] || acc.username);
    acc.password = acc.password.replace(/\${(.*?)}/g, (_, v) => process.env[v] || acc.password);
    return acc;
});

async function run() {
    const connector = new AcademicConnector();
    connector.restAdapter.baseUrl = 'https://api.neosia.unhas.ac.id';
    
    // We only process the 5 newly added accounts
    const targetAccounts = [
        "fib_sas_jepang", 
        "fib_sas_prancis", 
        "fib_pariwisata", 
        "fib_sas_daerah", 
        "fib_ilmu_sejarah"
    ];

    let allCollectedData = [];

    for (const accId of targetAccounts) {
        const account = config.accounts.find(a => a.id === accId);
        if(!account) {
            console.error(`Account ${accId} not found in config!`);
            continue;
        }
        
        console.log(`\n============================`);
        console.log(`Logging in via Puppeteer/Playwright for ${account.program_studi}...`);
        try {
            const tokens = await connector.browserAdapter.captureSessionToken(account);
            if(!tokens || !tokens.bearerToken) {
                console.error(`Failed to scrape auth token for ${accId}`);
                continue;
            }
            console.log(`SUCCESS! Bearer token acquired.`);

            // Get all active semesters for this account scope
            console.log(`Fetching active semesters...`);
            const psUrl = 'https://api.neosia.unhas.ac.id/api/admin/prodi_semester?filters[is_used]=1';
            const psData = await connector.restAdapter.get(psUrl, { bearerToken: tokens.bearerToken });
            
            const psArr = psData.prodiSemesters || psData.data || [];
            console.log(`Found ${psArr.length} semesters, scraping PA data for each...`);
            
            let accountPAData = [];
            for (const ps of psArr) {
                const idSem = ps.id || ps.id_prodi_semester;
                if(!idSem) continue;
                
                await new Promise(r => setTimeout(r, 2000)); // Rate limit bypass
                
                const paUrl = `https://api.neosia.unhas.ac.id/api/admin/penasihat_akademik?filters[id_prodi_semester]=${idSem}`;
                const paData = await connector.restAdapter.get(paUrl, { bearerToken: tokens.bearerToken });
                
                let paArr = paData.dosens || paData.penasihat_akademiks || paData.data || [];
                if(!Array.isArray(paArr)) paArr = paArr.data || [];
                accountPAData.push(...paArr);
            }
            
            console.log(`Extracted total ${accountPAData.length} valid PA allocations for ${account.program_studi}.`);
            allCollectedData.push(...accountPAData);
            
        } catch (err) {
            console.error(`Error scraping data for ${accId}:`, err);
        }
    }
    
    // Dump massive array to file
    fs.writeFileSync('pa_dump_all.json', JSON.stringify(allCollectedData, null, 2));
    console.log(`\nALL DONE! Extracted data for ${allCollectedData.length} total PA records globally to pa_dump_all.json`);
    
    // Close browser if dangling
    process.exit(0);
}
run();
