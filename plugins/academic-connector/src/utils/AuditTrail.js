import fs from 'fs';
import path from 'path';

/**
 * AuditTrail — Appends undeniable transactional history specific to accounts.
 */
export class AuditTrail {
    constructor(logDir = './logs') {
        this.logDir = logDir;
        if (!fs.existsSync(this.logDir)) {
            fs.mkdirSync(this.logDir, { recursive: true });
        }
    }

    log(accountId, action, status, message = "") {
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 16);
        const logLine = `${timestamp} [${action}] [${accountId}] ${status} ${message}\n`;
        
        fs.appendFileSync(path.join(this.logDir, 'audit.log'), logLine);
    }
}
