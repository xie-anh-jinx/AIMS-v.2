import { RestAdapter } from './src/adapters/RestAdapter.js';
import { SessionManager } from './src/core/SessionManager.js';
import { NeoSIAClient } from './src/clients/NeoSIAClient.js';

(async () => {
    const logger = { info: console.log, warn: console.warn, error: console.error, debug: console.log };
    const rest = new RestAdapter({ maxRetries: 1 }, logger);
    const session = new SessionManager(rest, logger);
    await session.initialize();
    
    // We will test on a known working account
    const client = new NeoSIAClient(rest, session, { id: 'fib_sas_prancis' }, './providers/fib_sas_prancis', logger);
    
    try {
        console.log("Fetching ALL Prodi_Semester without id_prodi filter...");
        const res = await rest.get('https://api.neosia.unhas.ac.id/api/admin/prodi_semester?filters[is_used]=1', session._getSession('fib_sas_prancis'));
        const data = res.data || res.items || res;
        if (Array.isArray(data) && data.length > 0) {
            console.log("Success! Found", data.length, "items.");
            console.log("Sample:", JSON.stringify(data[0], null, 2));
            console.log("ID Prodi_Semester to use:", data[0].id_prodi_semester || data[0].id);
        } else {
            console.log("Empty or no array:", JSON.stringify(res).substring(0, 500));
        }
    } catch (e) {
        console.error("Error fetching prodi_semester:", e.message);
    }
    
    process.exit(0);
})();
