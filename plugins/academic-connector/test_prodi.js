import * as dotenv from 'dotenv';
dotenv.config();
import { AcademicConnector } from './src/AcademicConnector.js';
import { NeoSIAClient } from './src/clients/NeoSIAClient.js';

async function main() {
    const sdk = new AcademicConnector();
    await sdk.initAccounts();
    const account = sdk.config.accounts[0];
    
    // Login
    const keys = await sdk.browserAdapter.captureSessionToken(account);
    sdk.sessionManager.registerSession(account.id, keys.bearerToken, keys.cookies);
    
    const client = new NeoSIAClient(sdk.restAdapter, sdk.sessionManager, account, `./providers/${sdk.config.provider}`, sdk.logger);
    
    let prodis = new Set();
    const data = await client.getStudents(2023);
    let students = Array.isArray(data) ? data : (data.mahasiswas || data.data || []);
    
    for (const s of students) {
        if (s.raw_prodi) prodis.add(s.raw_prodi.toUpperCase());
    }
    console.log("Unique Prodis from remote API Angkatan 2023:");
    console.log(Array.from(prodis));
}
main().catch(console.error);
