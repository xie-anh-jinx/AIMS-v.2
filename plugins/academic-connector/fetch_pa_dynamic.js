import { RestAdapter } from './src/adapters/RestAdapter.js';
import { SessionManager } from './src/core/SessionManager.js';
import { NeoSIAClient } from './src/clients/NeoSIAClient.js';
import { DatabaseAdapter } from './src/adapters/DatabaseAdapter.js';

(async () => {
    const logger = { info: console.log, warn: console.warn, error: console.error, debug: console.log };
    const rest = new RestAdapter({ maxRetries: 1 }, logger);
    const session = new SessionManager(rest, logger);
    const db = new DatabaseAdapter(process.env.DATABASE_URL, logger);
    
    // Asumsi token di load dari out.log atau dump-rendered.html
    // Namun karena saya ingin tes utuh, saya akan pakai SessionManager load dari DB?
    // Tunggu, SessionManager load dari sqlite.
    await session.initialize();
    
    const tokenData = await session.getToken('fib_sas_prancis');
    if (!tokenData) {
        console.log("No token! Run example.js first.");
        return;
    }
    
    const client = new NeoSIAClient(rest, session, { id: 'fib_sas_prancis' }, './providers/fib_sas_prancis', logger);
    
    try {
        console.log("Fetching Prodi Semester for PRODI 33...");
        const prodiRes = await client.getProdiSemester(33);
        console.log("Prodi Data Keys:", Object.keys(prodiRes));
        console.log("Prodi Data [0]:", JSON.stringify(prodiRes.data ? prodiRes.data[0] : prodiRes[0]));

        const id_prodi_semester = 3600; // As user specified
        console.log(`Fetching PA for Semester ${id_prodi_semester}...`);
        const paRes = await client.getPenasihatAkademik(id_prodi_semester);
        console.log("PA Payload Array Keys:", Object.keys(paRes));
        const arr = paRes.data || paRes.items || paRes;
        if (Array.isArray(arr) && arr.length > 0) {
            console.log("PA Profile [0]:", JSON.stringify(arr[0], null, 2));
        } else {
            console.log("PA is empty or not iterable?", JSON.stringify(arr));
        }

    } catch (e) {
        console.error("Error:", e.message);
    }
    
    process.exit(0);
})();
