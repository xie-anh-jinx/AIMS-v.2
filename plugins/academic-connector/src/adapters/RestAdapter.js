import fetch from 'node-fetch';
import http from 'http';
import https from 'https';

const httpAgent = new http.Agent({ keepAlive: true, maxSockets: 10 });
const httpsAgent = new https.Agent({ keepAlive: true, maxSockets: 10 });

/**
 * RestAdapter — High speed raw JSON executor using SessionManager's tokens.
 */
export class RestAdapter {
    constructor(logger) {
        this.logger = logger;
    }

    async get(url, sessionParams = {}) {
        const headers = { 'Content-Type': 'application/json' };
        
        if (sessionParams.bearerToken) {
            headers['Authorization'] = sessionParams.bearerToken;
        }
        
        if (sessionParams.cookies) {
            headers['Cookie'] = sessionParams.cookies;
        }
        
        this.logger?.debug(`[REST] GET ${url}`);
        
        const response = await fetch(url, {
            method: 'GET',
            headers: headers,
            agent: url.startsWith('https') ? httpsAgent : httpAgent
        });

        if (!response.ok) {
            throw new Error(`[REST] Error ${response.status}: ${await response.text()}`);
        }

        return await response.json();
    }

    // ==========================================
    // PROTOKOL KEAMANAN AIMS (READ-ONLY LOCK)
    // ==========================================
    
    _securityVeto(method) {
        this.logger?.error(`[SECURITY_VETO] Aksi eksekusi ${method} dilarang keras!`);
        throw new Error(`[SECURITY_VETO] AIMS Enterprise Connector is operating in strict READ-ONLY mode. \nKonektor AIMS HANYA memiliki izin untuk "membaca" dari portal universitas. Mutasi data melalui REST API ini secara otomatis diblokir oleh sistem keamanan AIMS Firewall demi integritas pangkalan data eksternal Universitas.`);
    }

    async post()   { this._securityVeto('POST'); }
    async put()    { this._securityVeto('PUT'); }
    async delete() { this._securityVeto('DELETE'); }
    async patch()  { this._securityVeto('PATCH'); }
}
