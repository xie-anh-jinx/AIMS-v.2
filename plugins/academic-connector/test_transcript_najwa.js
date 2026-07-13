import * as dotenv from 'dotenv';
dotenv.config({ path: '../../.env' });
import fs from 'fs';
import YAML from 'yaml';
import { AcademicConnector } from './src/AcademicConnector.js';
import { NeoSIAClient } from './src/clients/NeoSIAClient.js';

const configRaw = fs.readFileSync('./config.yml', 'utf8');
const cfgBase = YAML.parse(configRaw);

async function main() {
    const sdk = new AcademicConnector();
    const account = cfgBase.accounts.find(a => a.id === 'fib_superadmin');
    
    // Acquire session manually since token was lost
    const tokens = await sdk.browserAdapter.captureSessionToken(account);
    const token = tokens.bearerToken;
    
    sdk.sessionManager.registerSession(account.id, token, tokens.cookies);
    const client = new NeoSIAClient(sdk.restAdapter, sdk.sessionManager, account, `./providers/generic`, {info: ()=> {}, warn: ()=> {}, error: ()=> {}, debug: ()=> {}});
    
    console.log("Fetching transcript for F031251018 (NAJWA)...");
    try {
        const transcript = await client.getTranscript("F031251018");
        console.log("Transcript details:");
        console.log("IPK:", transcript.ipk);
        console.log("Total SKS:", transcript.total_sks);
    } catch(e) {
        console.error("FAIL:", e.message);
    }
}
main().catch(console.error);
