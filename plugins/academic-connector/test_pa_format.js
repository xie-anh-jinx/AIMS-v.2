import { RestAdapter } from './src/adapters/RestAdapter.js';
import { SessionManager } from './src/core/SessionManager.js';
import { NeoSIAClient } from './src/clients/NeoSIAClient.js';

(async () => {
    const logger = { info: console.log, warn: console.warn, error: console.error, debug: console.log };
    const rest = new RestAdapter({ maxRetries: 1 }, logger);
    const session = new SessionManager(rest, logger);
    await session.initialize();
    
    // Test on Pariwisata account
    const idSem = 4036; 
    const client = new NeoSIAClient(rest, session, { id: 'fib_pariwisata' }, './providers/fib_pariwisata', logger);
    
    try {
        console.log(`Fetching PA for Semester ${idSem}...`);
        const paRes = await client.getPenasihatAkademik(idSem);
        let arr = paRes;
        if (paRes && typeof paRes === 'object' && !Array.isArray(paRes)) {
            arr = paRes.penasihat_akademiks || paRes.penasihatAkademiks || paRes.data || paRes.items || paRes.list || paRes.dosen || Object.values(paRes).find(v => Array.isArray(v)) || [];
        }
        if (Array.isArray(arr) && arr.length > 0) {
            console.log("Found PA Count:", arr.length);
            console.log("Sample PA [0]:", JSON.stringify(arr[0], null, 2));
        } else {
            console.log("PA is empty.", JSON.stringify(paRes));
        }
    } catch (e) {
        console.error("Error fetching PA:", e.message);
    }
    
    process.exit(0);
})();
