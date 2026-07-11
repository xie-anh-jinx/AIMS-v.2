/**
 * SessionManager — Central Pool for Multi-Account Authentication Sessions
 */
export class SessionManager {
    constructor(logger) {
        this.logger = logger;
        this.pool = new Map(); // Map<accountId, sessionContext>
    }

    /**
     * registerSession stores extracted bearer and cookies mapping to an account.
     */
    registerSession(accountId, bearerToken, cookies) {
        this.pool.set(accountId, {
            bearerToken,
            cookies,
            timestamp: Date.now()
        });
        this.logger?.audit(`[Auth] Session registered for account: ${accountId}`);
    }

    getSession(accountId) {
        return this.pool.get(accountId);
    }

    hasValidSession(accountId) {
        const session = this.pool.get(accountId);
        if (!session) return false;
        
        // Simulating expiry after 60 min for POC
        const isExpired = (Date.now() - session.timestamp) > (60 * 60 * 1000);
        return !isExpired;
    }

    clearSession(accountId) {
        this.pool.delete(accountId);
        this.logger?.audit(`[Auth] Session cleared for account: ${accountId}`);
    }
}
