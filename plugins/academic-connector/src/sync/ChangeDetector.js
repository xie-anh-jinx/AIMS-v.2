import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

/**
 * ChangeDetector — Compares newly fetched academic records with stored state to emit mutations.
 */
export class ChangeDetector {
    constructor(logger) {
        this.logger = logger;
        this.cacheFile = path.resolve(process.cwd(), '.delta_cache.json');
        this.stateDb = new Map();
        
        if (fs.existsSync(this.cacheFile)) {
            try {
                const data = JSON.parse(fs.readFileSync(this.cacheFile, 'utf8'));
                this.stateDb = new Map(Object.entries(data));
            } catch (e) {
                this.logger?.warn("[ChangeDetector] Failed to load cache, starting fresh.");
            }
        }
    }

    _save() {
        fs.writeFileSync(this.cacheFile, JSON.stringify(Object.fromEntries(this.stateDb)), 'utf8');
    }

    _hash(data) {
        const { raw_prodi, ...hashData } = data;
        return crypto.createHash('md5').update(JSON.stringify(hashData)).digest('hex');
    }

    detectChanges(newRecord) {
        const studentId = newRecord.student_id;
        const newHash = this._hash(newRecord);
        const oldHash = this.stateDb.get(studentId);

        if (!oldHash) {
            this.stateDb.set(studentId, newHash);
            this._save();
            this.logger?.debug(`[Diff API] New student detected: ${studentId}`);
            return { changed: true, reason: 'NEW_RECORD' };
        }

        if (oldHash !== newHash) {
            this.stateDb.set(studentId, newHash);
            this._save();
            this.logger?.debug(`[Diff API] Data mutation detected for: ${studentId}`);
            return { changed: true, reason: 'UPDATED_RECORD' };
        }

        return { changed: false, reason: 'UNCHANGED' };
    }
}
