import fs from 'fs';
import path from 'path';

const LEVELS = { debug: 0, info: 1, warn: 2, error: 3, audit: 4, sync: 5 };
const COLORS = { debug: '\x1b[90m', info: '\x1b[36m', warn: '\x1b[33m', error: '\x1b[31m', audit: '\x1b[35m', sync: '\x1b[32m', reset: '\x1b[0m' };

class Logger {
    constructor(options = {}) {
        this.prefix = options.prefix || 'Connector';
        this.level = options.level || 'info';
        this.logDir = options.path || './logs';
        this.logs = [];

        fs.mkdirSync(path.resolve(this.logDir), { recursive: true });
    }

    _shouldLog(level) {
        return LEVELS[level] >= LEVELS[this.level];
    }

    _format(level, message) {
        const ts = new Date().toISOString();
        return `${ts} [${level.toUpperCase().padEnd(5)}] [${this.prefix}] ${message}`;
    }

    _write(level, message) {
        if (!this._shouldLog(level)) return;
        const formatted = this._format(level, message);
        this.logs.push(formatted);

        const color = COLORS[level] || COLORS.info;
        console.log(`${color}${formatted}${COLORS.reset}`);

        // Write to specific log file
        const logFile = path.resolve(this.logDir, `${level}.log`);
        fs.appendFileSync(logFile, formatted + '\n');

        // Also write to events.log (combined)
        const eventsFile = path.resolve(this.logDir, 'events.log');
        fs.appendFileSync(eventsFile, formatted + '\n');
    }

    debug(message) { this._write('debug', message); }
    info(message)  { this._write('info', message); }
    warn(message)  { this._write('warn', message); }
    error(message) { this._write('error', message); }

    audit(message, meta = {}) {
        const metaStr = Object.keys(meta).length > 0 ? ` | ${JSON.stringify(meta)}` : '';
        this._write('audit', `${message}${metaStr}`);
    }

    sync(message, meta = {}) {
        const metaStr = Object.keys(meta).length > 0 ? ` | ${JSON.stringify(meta)}` : '';
        this._write('sync', `${message}${metaStr}`);
    }

    getLogs() {
        return this.logs.join('\n');
    }

    flush(filename) {
        const target = filename || `connector-log-${Date.now()}.txt`;
        fs.writeFileSync(path.resolve(this.logDir, target), this.getLogs());
    }
}

export function createLogger(options = {}) {
    return new Logger(options);
}

export default Logger;
