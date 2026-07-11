import * as dotenv from 'dotenv';
dotenv.config();
import { AcademicConnector } from './src/AcademicConnector.js';
import { NeoSIAClient } from './src/clients/NeoSIAClient.js';

async function main() {
    const sdk = new AcademicConnector();
    await sdk.initAccounts();
    const account = sdk.config.accounts[0];
    const keys = await sdk.browserAdapter.captureSessionToken(account);
    sdk.sessionManager.registerSession(account.id, keys.bearerToken, keys.cookies);
    
    const client = new NeoSIAClient(sdk.restAdapter, sdk.sessionManager, account, `./providers/${sdk.config.provider}`, sdk.logger);
    
    console.log("Fetching transcript for F011171001...");
    try {
        const transcript = await client.getTranscript("F011171001");
        console.log(transcript);
    } catch(e) {
        console.error("FAIL:", e.message);
    }
}
main().catch(console.error);
