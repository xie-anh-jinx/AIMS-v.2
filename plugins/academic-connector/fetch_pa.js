import fs from 'fs';
import YAML from 'yaml';
import { AcademicConnector } from './src/AcademicConnector.js';

const config = YAML.parse(fs.readFileSync('./config.yml', 'utf8'));

async function run() {
    const connector = new AcademicConnector();
    
    // Login fib_sas_prancis
    const account = config.accounts.find(a => a.id === "fib_sas_prancis");
    
    console.log("Logging in...");
    const tokens = await connector.browserAdapter.captureSessionToken(account);
    console.log("Tokens ready:", !!tokens.bearerToken);
    
    // Set explicit baseUrl
    connector.restAdapter.baseUrl = 'https://api.neosia.unhas.ac.id';

    const url = 'https://api.neosia.unhas.ac.id/api/admin/penasihat_akademik?filters[id_prodi_semester]=3600';
    try {
        const data = await connector.restAdapter.get(url, { bearerToken: tokens.bearerToken });
        console.log("RESPONSE DATA DUMP:");
        console.log(JSON.stringify(data.data[0] || data[0] || data, null, 2));
    } catch (err) {
        console.error(err);
    }
}
run();
