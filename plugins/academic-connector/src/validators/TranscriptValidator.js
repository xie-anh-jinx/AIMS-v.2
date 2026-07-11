/**
 * TranscriptValidator — Validates extracted transcript records.
 * Rejects rows with missing NIM, invalid IPK, etc.
 */
export class TranscriptValidator {
    constructor(validationConfig, logger) {
        this.config = validationConfig || {};
        this.logger = logger;
    }

    validate(records) {
        this.logger?.info(`Validating ${records.length} records...`);
        const valid = [];
        const rejected = [];

        for (const record of records) {
            const errors = this._check(record);
            if (errors.length === 0) {
                valid.push(record);
            } else {
                rejected.push({ record, errors });
                this.logger?.warn(`Rejected record: ${JSON.stringify(errors)}`);
            }
        }

        this.logger?.info(`Validation complete: ${valid.length} valid, ${rejected.length} rejected.`);
        return { valid, rejected };
    }

    _check(record) {
        const errors = [];

        if (this.config.requireNIM && !record.student_id && !record.nim) {
            errors.push('NIM/student_id kosong');
        }

        if (this.config.requireIPK) {
            const ipk = parseFloat(record.cumulative_gpa || record.ipk);
            if (isNaN(ipk)) {
                errors.push('IPK tidak valid');
            } else if (ipk < 0 || ipk > 4.0) {
                errors.push(`IPK di luar jangkauan: ${ipk}`);
            }
        }

        if (this.config.skipEmptyRow) {
            const values = Object.values(record).filter(v => v !== null && v !== '');
            if (values.length === 0) {
                errors.push('Baris kosong');
            }
        }

        return errors;
    }
}
