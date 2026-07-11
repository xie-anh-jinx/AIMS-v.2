import { Mapper } from '../../utils/mapper.js';

/**
 * TranscriptTransformer — Transforms raw portal data to AIMS-standard format.
 */
export class TranscriptTransformer {
    constructor(mappingPath, logger) {
        this.mapper = new Mapper(mappingPath);
        this.logger = logger;
    }

    transform(records) {
        this.logger?.info(`Transforming ${records.length} records...`);
        const transformed = this.mapper.mapAll(records);

        // Normalize numeric fields
        return transformed.map(record => ({
            ...record,
            semester_gpa: record.semester_gpa ? parseFloat(record.semester_gpa) : null,
            cumulative_gpa: record.cumulative_gpa ? parseFloat(record.cumulative_gpa) : null,
            total_credits: record.total_credits ? parseInt(record.total_credits, 10) : null,
            semester: record.semester ? parseInt(record.semester, 10) : null,
            enrollment_year: record.enrollment_year ? parseInt(record.enrollment_year, 10) : null
        }));
    }
}
