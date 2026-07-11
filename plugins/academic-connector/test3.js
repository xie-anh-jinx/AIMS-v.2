import fs from 'fs';
import YAML from 'yaml';
import { HttpClient } from './src/HttpClient.js';
import { SessionManager } from './src/auth/SessionManager.js';
import { BrowserAdapter } from './src/adapters/BrowserAdapter.js';
import { NeoSIAClient } from './src/clients/NeoSIAClient.js';
import dotenv from 'dotenv';
dotenv.config();

(async () => {
    try {
        const logger = { info: console.log, warn: console.log, error: console.error, audit: console.log };
        const config = YAML.parse(fs.readFileSync('config.yml', 'utf8'));
        const account = config.accounts[0];
        account.username = process.env.VITE_AIMS_USER || 'admin';
        account.password = process.env.VITE_AIMS_PASS || 'admin'; // just dummy, we don't know the env. Let's just grep the actual log!
    } catch(e) {}
})();
