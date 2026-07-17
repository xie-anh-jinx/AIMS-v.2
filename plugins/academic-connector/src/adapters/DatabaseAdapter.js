import pkg from 'pg';
const { Pool } = pkg;

export class DatabaseAdapter {
    constructor(connectionString, logger) {
        this.logger = logger;
        this.pool = new Pool({
            connectionString: connectionString,
            max: 10,
            idleTimeoutMillis: 30000,
        });

        // Test koneksi
        this.pool.on('error', (err, client) => {
            this.logger.error(`[DB] Unexpected error on idle client: ${err.message}`);
            process.exit(-1);
        });
    }

    async upsertStudent(nim, nama, angkatan, prodi, status = 'Aktif') {
        const client = await this.pool.connect();
        try {
            // Kalkulasi kasaran semester untuk GUI AIMS Dashboard
            const mockSemester = Math.max(1, (2026 - angkatan) * 2);
            
            const query = `
                INSERT INTO students (nim, nama, angkatan, prodi, status, semester, email, nomor_whatsapp)
                VALUES ($1, $2, $3, $4, $5, $6, '', '')
                ON CONFLICT (nim) 
                DO UPDATE SET 
                    nama = EXCLUDED.nama,
                    angkatan = EXCLUDED.angkatan,
                    prodi = EXCLUDED.prodi,
                    status = EXCLUDED.status,
                    semester = EXCLUDED.semester,
                    email = EXCLUDED.email,
                    nomor_whatsapp = EXCLUDED.nomor_whatsapp
                RETURNING id;
            `;
            
            const values = [nim, nama, angkatan, prodi, status, mockSemester];
            const result = await client.query(query, values);
            const studentDbId = result.rows[0].id;

            this.logger.debug(`[DB] Upserted Student ${nim} (DB ID: ${studentDbId})`);
            return studentDbId;

        } catch (error) {
            this.logger.error(`[DB] Error Upsert Student: ${error.message}`);
            throw error;
        } finally {
            client.release();
        }
    }

    async upsertAcademicRecord(studentDbId, ipk, total_credits) {
        const client = await this.pool.connect();
        try {
            // Ambil semester aktif mahasiswa
            const res = await client.query('SELECT semester FROM students WHERE id = $1', [studentDbId]);
            const semesterAktif = res.rows[0]?.semester || 5;
            
            // Check jika data sudah ada untuk student_id dan semester tersebut
            const checkQuery = `SELECT id FROM academic_records WHERE student_id = $1 AND semester = $2`;
            const existing = await client.query(checkQuery, [studentDbId, semesterAktif]);
            
            if (existing.rows.length > 0) {
                const updateQuery = `UPDATE academic_records SET ipk = $1, sks = $2 WHERE id = $3`;
                await client.query(updateQuery, [ipk, total_credits, existing.rows[0].id]);
                this.logger.debug(`[DB] Updated Academic Record for Student ID ${studentDbId} (Semester: ${semesterAktif})`);
            } else {
                const insertQuery = `INSERT INTO academic_records (student_id, semester, ipk, sks, status) VALUES ($1, $2, $3, $4, 'TEREKAM')`;
                await client.query(insertQuery, [studentDbId, semesterAktif, ipk, total_credits]);
                this.logger.debug(`[DB] Inserted Academic Record for Student ID ${studentDbId} (Semester: ${semesterAktif})`);
            }
        } catch (error) {
            this.logger.warn(`[DB] Academic Record insert/update terlewati: ${error.message}`);
        } finally {
            client.release();
        }
    }

    async upsertCourse(kode, nama, sks, semester) {
        const client = await this.pool.connect();
        try {
            const query = `
                INSERT INTO courses (kode, nama, sks, semester)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (kode) 
                DO UPDATE SET 
                    nama = EXCLUDED.nama,
                    sks = EXCLUDED.sks,
                    semester = EXCLUDED.semester
                RETURNING id;
            `;
            const result = await client.query(query, [kode, nama, sks, semester]);
            return result.rows[0].id;
        } catch (err) {
            this.logger.error(`[DB Adapter] Gagal upsert Course ${kode}: ${err.message}`);
            throw err;
        } finally {
            client.release();
        }
    }
    
    async upsertGrade(studentDbId, courseDbId, semester, grade, bobot) {
        const client = await this.pool.connect();
        try {
            const checkQuery = `SELECT id FROM grades WHERE student_id = $1 AND course_id = $2 AND semester = $3`;
            const existing = await client.query(checkQuery, [studentDbId, courseDbId, semester]);
            
            if (existing.rows.length > 0) {
                const updateQuery = `UPDATE grades SET grade = $1, bobot = $2 WHERE id = $3`;
                await client.query(updateQuery, [grade, bobot, existing.rows[0].id]);
            } else {
                const insertQuery = `INSERT INTO grades (student_id, course_id, semester, grade, bobot) VALUES ($1, $2, $3, $4, $5)`;
                await client.query(insertQuery, [studentDbId, courseDbId, semester, grade, bobot]);
            }
        } catch (err) {
            this.logger.error(`[DB Adapter] Gagal upsert Grade: ${err.message}`);
        } finally {
            client.release();
        }
    }

    async upsertAdvisor(nip, nama) {
        const client = await this.pool.connect();
        try {
            const defaultHash = '$2b$12$FCMiEQZ3wTWHR8oa47TE4ODtJUoiI/Tger84vjJsS6GAbAa/m5bVS'; // bcrypt 'password123'
            
            // 1. Create or GET User (Username = NIP)
            const uRes = await client.query('SELECT id FROM users WHERE username = $1', [nip]);
            let userId;
            if (uRes.rows.length === 0) {
                const uIns = await client.query(
                    'INSERT INTO users (username, hashed_password, role) VALUES ($1, $2, $3) RETURNING id',
                    [nip, defaultHash, 'ADVISOR']
                );
                userId = uIns.rows[0].id;
            } else {
                userId = uRes.rows[0].id;
            }

            // 2. Create or GET Advisor
            const aRes = await client.query('SELECT id FROM advisors WHERE user_id = $1', [userId]);
            let advisorId;
            if (aRes.rows.length === 0) {
                const aIns = await client.query(
                    'INSERT INTO advisors (user_id, nama) VALUES ($1, $2) RETURNING id',
                    [userId, nama]
                );
                advisorId = aIns.rows[0].id;
            } else {
                advisorId = aRes.rows[0].id;
            }
            return advisorId;
        } catch (e) {
            this.logger.error(`[DB] Error Upsert Advisor: ${e.message}`);
            throw e;
        } finally {
            client.release();
        }
    }

    async assignAdvisor(nim, advisorId) {
        const client = await this.pool.connect();
        try {
            await client.query('UPDATE students SET advisor_id = $1 WHERE nim = $2', [advisorId, nim]);
        } catch (e) {
            this.logger.error(`[DB] Error Assign Advisor to ${nim}: ${e.message}`);
            throw e;
        } finally {
            client.release();
        }
    }

    async getStudentNimsWithGrades() {
        const client = await this.pool.connect();
        try {
            const query = `
                SELECT DISTINCT s.nim 
                FROM students s 
                JOIN grades g ON s.id = g.student_id;
            `;
            const res = await client.query(query);
            return new Set(res.rows.map(r => r.nim));
        } catch (e) {
            this.logger.error(`[DB] Error fetching student nims with grades: ${e.message}`);
            return new Set();
        } finally {
            client.release();
        }
    }
}
