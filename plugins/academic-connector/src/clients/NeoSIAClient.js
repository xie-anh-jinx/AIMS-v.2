import fs from 'fs';
import path from 'path';
import YAML from 'yaml';

/**
 * NeoSIAClient — Wraps the Neosia API endpoints hiding URLs from Actions.
 */
export class NeoSIAClient {
    constructor(restAdapter, sessionManager, account, providerDir, logger) {
        this.rest = restAdapter;
        this.sessionManager = sessionManager;
        this.account = account;
        this.accountId = account.id;
        this.logger = logger;
        
        // Load Routes
        const routePath = path.join(providerDir, 'routes.yml');
        const fileData = fs.readFileSync(routePath, 'utf8');
        this.routesData = YAML.parse(fileData);
        this.baseUrl = this.routesData.api_base || new URL(this.routesData.login_portal).origin;
    }

    _getSession() {
        const sess = this.sessionManager.getSession(this.accountId);
        if (!sess) throw new Error(`[NeoSIAClient] No active session for account ${this.accountId}`);
        return sess;
    }

    async getStudents(angkatan = 2025) {
        const session = this._getSession();
        let route = this.routesData.routes.students.path;
        
        // Menambahkan filter admin jika terdapat identifier prodi
        if (this.account.id_prodi) {
            route += `?filters[id_prodi]=${this.account.id_prodi}&filters[angkatan]=${angkatan}`; 
        } else {
            route += `?filters[angkatan]=${angkatan}`;
        }
        
        return await this.rest.get(`${this.baseUrl}${route}`, session);
    }

    async getTranscript(nim) {
        const session = this._getSession();
        const route = this.routesData.routes.transcript.path;
        return await this.rest.get(`${this.baseUrl}${route}?nim=${nim}`, session);
    }
    
    async getKHS(nim, semester) {
        const session = this._getSession();
        const route = this.routesData.routes.khs.path;
        return await this.rest.get(`${this.baseUrl}${route}?nim=${nim}&semester=${semester}`, session);
    }
    
    async getProgress(nim) {
        const session = this._getSession();
        const route = this.routesData.routes.progress.path;
        return await this.rest.get(`${this.baseUrl}${route}?nim=${nim}`, session);
    }
    
    async getPenasihatAkademik(id_prodi_semester) {
        // According to user: https://api.neosia.unhas.ac.id/api/admin/penasihat_akademik?filters[id_prodi_semester]=...
        const session = this._getSession();
        return await this.rest.get(`${this.baseUrl}/api/admin/penasihat_akademik?filters[id_prodi_semester]=${id_prodi_semester}`, session);
    }
    
    async getProdiSemester(id_prodi) {
        // According to user: https://api.neosia.unhas.ac.id/api/admin/prodi_semester?filters[id_prodi]=33&filters[is_used]=1
        const session = this._getSession();
        return await this.rest.get(`${this.baseUrl}/api/admin/prodi_semester?filters[id_prodi]=${id_prodi}&filters[is_used]=1`, session);
    }
}
