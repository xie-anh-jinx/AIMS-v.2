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

    detectChanges(newRecord, nimsWithGrades = null) {
        const studentId = newRecord.student_id;
        const newHash = this._hash(newRecord);
        const oldHash = this.stateDb.get(studentId);
        
        // Force synchronization if student has no transcripts (no grades) in local DB
        const hasGrades = nimsWithGrades ? nimsWithGrades.has(studentId) : true;

        if (!oldHash) {
            return { changed: true, reason: 'NEW_RECORD', newHash };
        }

        if (oldHash !== newHash) {
            return { changed: true, reason: 'UPDATED_RECORD', newHash };
        }

        if (!hasGrades) {
            return { changed: true, reason: 'MISSING_TRANSCRIPT_RETRY', newHash };
        }

        return { changed: false, reason: 'UNCHANGED' };
    }

    commitChange(studentId, newHash) {
        this.stateDb.set(studentId, newHash);
        this._save();
        this.logger?.debug(`[ChangeDetector] State committed for: ${studentId}`);
    }
}
