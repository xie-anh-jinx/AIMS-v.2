import fs from 'fs';
import path from 'path';
import YAML from 'yaml';

/**
 * Maps raw extracted data fields to AIMS-standard fields using mapping.yml
 */
export class Mapper {
    constructor(mappingPath) {
        const raw = fs.readFileSync(path.resolve(mappingPath), 'utf8');
        this.mapping = YAML.parse(raw);
    }

    /**
     * Transform a single record using the mapping rules.
     * @param {Object} record - Raw record from portal (e.g. {nim: '123', ipk: '3.5'})
     * @returns {Object} - AIMS-standard record (e.g. {student_id: '123', cumulative_gpa: '3.5'})
     */
    mapRecord(record) {
        const mapped = {};
        for (const [portalKey, aimsKey] of Object.entries(this.mapping)) {
            if (record[portalKey] !== undefined) {
                mapped[aimsKey] = record[portalKey];
            }
        }
        return mapped;
    }

    /**
     * Transform an array of records.
     */
    mapAll(records) {
        return records.map(r => this.mapRecord(r));
    }

    /**
     * Get the reverse mapping (AIMS → Portal).
     */
    getReverseMapping() {
        const reversed = {};
        for (const [k, v] of Object.entries(this.mapping)) {
            reversed[v] = k;
        }
        return reversed;
    }
}
