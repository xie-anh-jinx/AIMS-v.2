import fetch from 'node-fetch';

/**
 * ServiceLayer — Orchestrates the full ETL pipeline (Extract → Validate → Transform → Sync).
 */
export class ServiceLayer {
    constructor({ extractor, validator, transformer, cache, eventBus, apiConfig, logger }) {
        this.extractor = extractor;
        this.validator = validator;
        this.transformer = transformer;
        this.cache = cache;
        this.eventBus = eventBus;
        this.apiConfig = apiConfig || {};
        this.logger = logger;
    }

    async syncTranscript() {
        const startTime = Date.now();

        // 1. Extract
        this.logger?.info('[Service] Step 1: Extracting data...');
        const rawData = await this.extractor.extract();

        // 2. Transform
        this.logger?.info('[Service] Step 2: Transforming data...');
        const transformed = this.transformer.transform(rawData);

        // 3. Validate
        this.logger?.info('[Service] Step 3: Validating data...');
        const { valid, rejected } = this.validator.validate(transformed);

        if (rejected.length > 0) {
            this.logger?.warn(`[Service] ${rejected.length} records rejected.`);
        }

        // 4. Filter cached (already synced)
        const toSync = valid.filter(record => {
            const id = record.student_id || record.nim;
            if (this.cache && this.cache.has('transcript', id)) {
                this.logger?.debug(`Skipping cached: ${id}`);
                return false;
            }
            return true;
        });

        // 5. Send to AIMS API
        this.logger?.info(`[Service] Step 4: Syncing ${toSync.length} records to AIMS...`);
        const endpoint = this.apiConfig.endpoint || 'http://localhost:8000/api/sync/transcript';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ records: toSync, syncedAt: new Date().toISOString() })
        });

        // 6. Update cache
        if (this.cache) {
            for (const record of toSync) {
                const id = record.student_id || record.nim;
                this.cache.set('transcript', id, record);
            }
        }

        // 7. Emit event
        const duration = ((Date.now() - startTime) / 1000).toFixed(2);
        const syncResult = {
            total: rawData.length,
            valid: valid.length,
            rejected: rejected.length,
            synced: toSync.length,
            skipped: valid.length - toSync.length,
            duration: `${duration}s`,
            httpStatus: response.status
        };

        this.logger?.sync('Transcript disinkronkan', syncResult);
        this.logger?.audit('SYNC_TRANSCRIPT', syncResult);

        await this.eventBus?.emit('TranscriptUpdated', syncResult);

        return syncResult;
    }
}
