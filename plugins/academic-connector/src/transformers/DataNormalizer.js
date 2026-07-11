/**
 * DataNormalizer — Standardizes responses from various University systems into AIMS JSON Schema.
 */
export class DataNormalizer {
    constructor(providerName, logger) {
        this.providerName = providerName;
        this.logger = logger;
    }

    normalizeStudent(rawRecord) {
        if (this.providerName === 'neosia') {
            let parsedStatus = 'Aktif';
            if (rawRecord.kode_status === 'C') parsedStatus = 'Cuti';
            else if (rawRecord.kode_status === 'L') parsedStatus = 'Lulus';
            else if (rawRecord.kode_status === 'D' || rawRecord.kode_status === 'DO') parsedStatus = 'Drop Out';
            else if (rawRecord.kode_status === 'N') parsedStatus = 'Non Aktif';
            else if (rawRecord.kode_status === 'A') parsedStatus = 'Aktif';
            
            return {
                student_id: rawRecord.nim || rawRecord.id_mhs,
                full_name: rawRecord.nama_mahasiswa || rawRecord.nama,
                academic_status: parsedStatus,
                cumulative_gpa: parseFloat(rawRecord.ipk || 0),
                total_credits: parseInt(rawRecord.sksTotal || 0, 10),
                raw_prodi: rawRecord.prodi ? rawRecord.prodi.nama_resmi : null
            };
        } else if (this.providerName === 'sikola') {
            return {
                student_id: rawRecord.student_number,
                full_name: rawRecord.full_name,
                cumulative_gpa: parseFloat(rawRecord.gpa || 0),
                total_credits: parseInt(rawRecord.total_credits || 0, 10)
            };
        }
        
        return rawRecord; // Fallback
    }

    normalizeTranscript(rawRecords) {
        if (!rawRecords.transkrips) return [];
        this.logger?.audit(`[Normalize] Normalized ${rawRecords.transkrips.length} transcript records for AIMS Schema.`);
        return rawRecords.transkrips.map(raw => ({
            course_code: raw.kode_mata_kuliah,
            course_name: raw.nama_mata_kuliah,
            credits: parseInt(raw.sks || 0, 10),
            semester: raw.semester ? parseInt(raw.semester.kode.substring(0,4)) : 1, // Fallback to year part of kode if we don't have int semester
            grade_letter: raw.nilai_huruf || 'E',
            grade_weight: parseFloat(raw.nilai_angka || 0)
        }));
    }
}
