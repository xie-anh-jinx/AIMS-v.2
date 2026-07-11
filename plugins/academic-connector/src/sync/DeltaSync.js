/**
 * DeltaSync — Iterates over lists and only pulls deep data for changed delta entities.
 */
export class DeltaSync {
    constructor(changeDetector, logger) {
        this.changeDetector = changeDetector;
        this.logger = logger;
    }

    async processBatch(rawStudentList, normalizer, deepFetchCallback, shallowPatchCallback = null) {
        let syncedCount = 0;
        let skippedCount = 0;

        for (const raw of rawStudentList) {
            const normalized = normalizer.normalizeStudent(raw);
            const diff = this.changeDetector.detectChanges(normalized);

            // Hanya tarik data spesifik transkrip jika Hash JSON dari rekap profil mahasiswa berubah (Atau mahasiswa baru)
            if (diff.changed) {
                this.logger?.audit(`[Delta Sync] Mutation detected for ${normalized.student_id} (${diff.reason}). Initiating deep fetch...`);
                await deepFetchCallback(normalized);
                syncedCount++;
            } else {
                skippedCount++;
                if (shallowPatchCallback) {
                    await shallowPatchCallback(normalized);
                }
            }
        }
        
        this.logger?.info(`[Delta Sync] Batch complete. Synced: ${syncedCount}, Skipped: ${skippedCount}`);
        return { syncedCount, skippedCount };
    }
}
