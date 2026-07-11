/**
 * StudentValidator — Validates student identity records.
 */
export class StudentValidator {
    constructor(logger) {
        this.logger = logger;
    }

    validate(students) {
        this.logger?.info(`Validating ${students.length} student records...`);
        const valid = [];
        const rejected = [];

        for (const student of students) {
            const errors = [];

            if (!student.student_id && !student.nim) {
                errors.push('Missing student_id/nim');
            }

            if (!student.full_name && !student.nama) {
                errors.push('Missing full_name/nama');
            }

            if (errors.length === 0) {
                valid.push(student);
            } else {
                rejected.push({ record: student, errors });
            }
        }

        this.logger?.info(`Students: ${valid.length} valid, ${rejected.length} rejected.`);
        return { valid, rejected };
    }
}
