import fs from 'fs';
import path from 'path';
import YAML from 'yaml';
import { createLogger } from '../utils/logger.js';
import { SessionManager } from './auth/SessionManager.js';
import { BrowserAdapter } from './adapters/BrowserAdapter.js';
import { RestAdapter } from './adapters/RestAdapter.js';
import { NeoSIAClient } from './clients/NeoSIAClient.js';
import { DataNormalizer } from './transformers/DataNormalizer.js';
import { ChangeDetector } from './sync/ChangeDetector.js';
import { DeltaSync } from './sync/DeltaSync.js';
import { IntelligentScheduler } from './scheduler/IntelligentScheduler.js';
import { AuditTrail } from './utils/AuditTrail.js';
import { DatabaseAdapter } from './adapters/DatabaseAdapter.js';

const FIB_PRODI_MAP = {
    'SASTRA INDONESIA - S1': 'Sastra Indonesia',
    'SASTRA INGGRIS - S1': 'Sastra Inggris',
    'SASTRA PRANCIS - S1': 'Sastra Prancis',
    'SASTRA ASIA BARAT - S1': 'Sastra Arab',
    'SASTRA ASIA BARAT / ARAB - S1': 'Sastra Arab',
    'SASTRA DAERAH B. BUGIS MAK - S1': 'Sastra Bugis Makassar',
    'SASTRA BUGIS-MAKASSAR - S1': 'Sastra Bugis Makassar',
    'ARKEOLOGI - S1': 'Arkeologi',
    'ILMU SEJARAH - S1': 'Sejarah',
    'SEJARAH - S1': 'Sejarah',
    'SASTRA JEPANG - S1': 'Sastra Jepang',
    'BAHASA MANDARIN DAN KEBUDAYAAN TIONGKOK - S1': 'Bahasa Mandarin & kebudayaan Tiongkok',
    'PARIWISATA - S1': 'Pariwisata',
    
    // Program Pascasarjana (S2/S3)
    'KAJIAN BUDAYA - S2': 'Kajian Budaya (S2)',
    'BAHASA INDONESIA - S2': 'Bahasa Indonesia (S2)',
    'ILMU LINGUISTIK - S3': 'Ilmu Linguistik (S3)',
    'ARKEOLOGI - S2': 'Arkeologi (S2)',
    'BAHASA INGGRIS - S2': 'Bahasa Inggris (S2)',
    'LINGUISTIK - S2': 'Linguistik (S2)',
    'SASTRA INDONESIA - S3': 'Sastra Indonesia (S3)',
    'SEJARAH - S2': 'Sejarah (S2)',
    'BAHASA INGGRIS - S3': 'Bahasa Inggris (S3)'
};

export class AcademicConnector {
    constructor() {
        this.config = YAML.parse(fs.readFileSync('./config.yml', 'utf8'));
        this.logger = createLogger({ prefix: 'V3-Engine', level: this.config.logging.level });
        this.audit = new AuditTrail(this.config.logging.path);
        
        this.sessionManager = new SessionManager(this.logger);
        this.scheduler = new IntelligentScheduler(this.logger);
        
        this.browserAdapter = new BrowserAdapter({ browser: this.config.browser, routes: this._loadRoutes() }, this.logger);
        this.restAdapter = new RestAdapter(this.logger);
        
        this.changeDetector = new ChangeDetector(this.logger);
        this.dataNormalizer = new DataNormalizer(this.config.provider, this.logger);
        this.deltaSync = new DeltaSync(this.changeDetector, this.logger);
        
        // Resolusi konfigurasi Vault ENV secara dinamik
        const dbUrl = process.env[this.config.database_url.slice(2, -1)] || this.config.database_url;
        this.dbAdapter = new DatabaseAdapter(dbUrl, this.logger);

        this.logger.info('[AIMS] Academic Connector V3 Initialized.');
    }

    _loadRoutes() {
        return YAML.parse(fs.readFileSync(`./providers/${this.config.provider}/routes.yml`, 'utf8'));
    }

    async initAccounts() {
        this.logger.info(`[Dispatcher] Loading ${this.config.accounts.length} accounts into Scheduler.`);
        
        for (const account of this.config.accounts) {
             // Deteksi pola ${VARIABEL} dan ganti nilainya dari file .env (process.env)
             // Jika Anda mengetikkan teks biasa (tanpa ${}), maka ia akan membacanya secara statis kelak.
             
             const resolveEnv = (val) => {
                 if (typeof val === 'string' && val.startsWith('${') && val.endsWith('}')) {
                     const envKey = val.slice(2, -1);
                     return process.env[envKey] || val; 
                 }
                 return val;
             };

             account.username = resolveEnv(account.username);
             account.password = resolveEnv(account.password);
             
             this.scheduler.enqueue(account);
        }
    }

    async executeMultiAccountSync() {
        await this.initAccounts();
        
        // Callback executor for each account
        await this.scheduler.start(async (account) => {
            this.audit.log(account.id, 'Sync Initiated', 'IN_PROGRESS');
            
            // 1. Check or Establish Session
            if (!this.sessionManager.hasValidSession(account.id)) {
                this.audit.log(account.id, 'Login', 'PENDING', 'Booting Headless Browser');
                
                try {
                    const keys = await this.browserAdapter.captureSessionToken(account);
                    this.sessionManager.registerSession(account.id, keys.bearerToken, keys.cookies);
                    this.audit.log(account.id, 'Login', 'SUCCESS');
                } catch (e) {
                    this.audit.log(account.id, 'Login', 'FAILED', e.message);
                    throw e; // Handled by Scheduler
                }
            }

            // 2. Fast REST Execution
            const client = new NeoSIAClient(this.restAdapter, this.sessionManager, account, `./providers/${this.config.provider}`, this.logger);
            
            try {
                this.audit.log(account.id, 'Data Synchronization', 'PENDING');
                
                let totalSynced = 0;
                
                // 3. Muat Data Penasihat Akademik (Dosen PA)
                let advisorMap = {}; // nim -> advisor_id
                try {
                    this.logger.info(`[Pipeline] Mengambil meta prodi_semester yang aktif...`);
                    // Fetch dynamic prodi_semester
                    const prodiSemRes = await client.rest.get(`${client.baseUrl}/api/admin/prodi_semester?filters[is_used]=1`, client._getSession());
                    let prodiSemList = prodiSemRes;
                    if (prodiSemRes && !Array.isArray(prodiSemRes)) {
                        prodiSemList = prodiSemRes.prodiSemesters || prodiSemRes.data || prodiSemRes.items || [];
                    }
                    
                    if (!Array.isArray(prodiSemList) || prodiSemList.length === 0) {
                        this.logger.warn(`[Pipeline] Gagal mendapatkan daftar prodi_semester: ${JSON.stringify(prodiSemRes).substring(0, 200)}`);
                    } else {
                        this.logger.info(`[Pipeline] Menemukan ${prodiSemList.length} semester aktif. Memuat peta PA...`);
                        
                        for (const ps of prodiSemList) {
                            const idSem = ps.id || ps.id_prodi_semester;
                            if (!idSem) continue;
                            
                            const paResponse = await client.getPenasihatAkademik(idSem);
                            
                            let paArray = paResponse;
                            if (paResponse && typeof paResponse === 'object' && !Array.isArray(paResponse)) {
                                paArray = paResponse.dosens || paResponse.penasihat_akademiks || paResponse.penasihatAkademiks || paResponse.data || paResponse.items || paResponse.list || paResponse.dosen || Object.values(paResponse).find(v => Array.isArray(v)) || [];
                            }
                            if (!Array.isArray(paArray)) {
                                continue;
                            }
                            
                            if (paArray.length > 0) {
                                // this.logger.info(`[DEBUG PA FULL_PAYLOAD] Sem ${idSem}: ${JSON.stringify(paResponse).substring(0, 100)}`);
                            }
                            
                            for (const paObj of paArray) {
                                // The new structure uses paObj.dosen and paObj.mahasiswas
                                const pa = paObj.dosen || paObj;
                                
                                const nip = (pa.nip || pa.id_pegawai || pa.username)?.toString();
                                if (!nip) continue;
                                
                                const nama = pa.nama_dosen || pa.nama || pa.nama_pegawai || ("Dosen " + nip);
                                const advisorId = await this.dbAdapter.upsertAdvisor(nip, nama);
                                
                                // Reset the mapped users to 'password123' just in case
                                await this.dbAdapter.pool.query("UPDATE users SET hashed_password = $1 WHERE username = $2", ['$2b$12$FCMiEQZ3wTWHR8oa47TE4ODtJUoiI/Tger84vjJsS6GAbAa/m5bVS', nip]);
                                
                                const mhsList = paObj.mahasiswas || paObj.mahasiswa || paObj.mahasiswa_bimbingan || paObj.bimbingan;
                                if (Array.isArray(mhsList)) {
                                    for (const mhs of mhsList) {
                                        const nimStr = (typeof mhs === 'string' ? mhs : (mhs.nim || mhs.id))?.toString();
                                        if (nimStr) advisorMap[nimStr] = advisorId;
                                    }
                                } 
                                else if (pa.nim || pa.id_mahasiswa) {
                                    const nimStr = (pa.nim || pa.id_mahasiswa).toString();
                                    advisorMap[nimStr] = advisorId;
                                }
                            }
                        }
                    }
                    this.logger.info(`[Pipeline] Peta PA Berhasil Diload: Terdapat ${Object.keys(advisorMap).length} relasi mahasiswa-dosen.`);
                } catch(err) {
                    this.logger.warn(`[Pipeline] Gagal memuat Peta Penasihat Akademik: ${err.message}`);
                }
                
                // Looping Penarikan Data (Menarik angkatan 2019-2025 agar mencakup semua data mahasiswa FIB)
                for (let angkatan = 2019; angkatan <= 2025; angkatan++) {
                    this.logger.info(`[Pipeline] Menarik data Angkatan ${angkatan}...`);
                    
                    const responsePayload = await client.getStudents(angkatan); 
                    
                    let studentArray = responsePayload;
                    if (!Array.isArray(responsePayload)) {
                        studentArray = responsePayload.mahasiswas || responsePayload.data || responsePayload.list || responsePayload.items || [];
                        
                        // [DEBUG INJECTION] Cetak struktur kunci JSON jika mahasiswa gagal dibongkar
                        if (studentArray.length === 0) {
                            this.logger.warn(`[Pipeline] Struktur JSON tak dikenal: ${JSON.stringify(Object.keys(responsePayload))}`);
                        }
                    }
                    
                    this.logger.info(`[Pipeline] Angkatan ${angkatan}: Menemukan ${studentArray.length} mahasiswa.`);
                    if (studentArray.length > 0 && angkatan === 2025) {
                        this.logger.warn(`[DEBUG_API] Neosia JSON Keys: ${Object.keys(studentArray[0]).join(', ')}`);
                    }
                    
                    if (studentArray.length > 0) {
                        const nimsWithGrades = await this.dbAdapter.getStudentNimsWithGrades();
                        
                        // Delta Sync mengekstrak dan melakukan normalisasi JSON internal
                        const syncReport = await this.deltaSync.processBatch(studentArray, this.dataNormalizer, async (studentObj) => {
                            const studentId = studentObj.student_id;
                            
                            // Guard Clause: Hanya proses mahasiswa dari Fakultas Ilmu Budaya (NIM berawalan 'F')
                            if (!studentId || !studentId.toUpperCase().startsWith('F')) {
                                return;
                            }
                            
                            const fullName = studentObj.full_name || ("Mahasiswa " + studentId);
                            
                            // Format Beautiful Prodi Name & Whitelist S1 FIB
                            let finalProdi = null;
                            if (studentObj.raw_prodi) {
                                const raw = studentObj.raw_prodi.toUpperCase();
                                if (raw.includes('MANDARIN')) {
                                    finalProdi = 'Bahasa Mandarin & kebudayaan Tiongkok';
                                } else {
                                    finalProdi = FIB_PRODI_MAP[raw];
                                }
                            }
                            
                            // Dynamic fallback for S2/S3 based on NIM prefixes
                            if (!finalProdi && studentId) {
                                const idUpper = studentId.toUpperCase();
                                if (idUpper.startsWith('F062')) finalProdi = 'Kajian Budaya (S2)';
                                else if (idUpper.startsWith('F032')) finalProdi = 'Bahasa Indonesia (S2)';
                                else if (idUpper.startsWith('F013')) finalProdi = 'Ilmu Linguistik (S3)';
                                else if (idUpper.startsWith('F042')) finalProdi = 'Arkeologi (S2)';
                                else if (idUpper.startsWith('F022')) finalProdi = 'Bahasa Inggris (S2)';
                                else if (idUpper.startsWith('F012')) finalProdi = 'Linguistik (S2)';
                                else if (idUpper.startsWith('F033')) finalProdi = 'Sastra Indonesia (S3)';
                                else if (idUpper.startsWith('F052')) finalProdi = 'Sejarah (S2)';
                                else if (idUpper.startsWith('F023')) finalProdi = 'Bahasa Inggris (S3)';
                            }
                            
                            if (!finalProdi) return; // Drop jika merupakan prodi S2/S3/Fakultas lain
 
                            let transcript = null;
                            const isOwnProdi = account.program_studi && 
                                (finalProdi.toLowerCase().includes(account.program_studi.toLowerCase()) || 
                                 account.program_studi.toLowerCase().includes(finalProdi.toLowerCase()) ||
                                 (account.program_studi.includes('Daerah') && finalProdi.includes('Bugis')) ||
                                 account.program_studi.toLowerCase().includes("fakultas"));
                            
                            if (isOwnProdi) {
                                try {
                                    transcript = await client.getTranscript(studentId);
                                    if (studentId === "F051171001" && transcript) {
                                        this.logger.warn(`[DEBUG_API_DUMP] ${JSON.stringify(transcript)}`);
                                    }
                                } catch (err) {
                                    this.logger.warn(`[Pipeline] Gagal menarik transkrip untuk ${studentId} (${err.message})`);
                                    throw err;
                                }
                            }

                            // Integrasi AIMS Akhir (Injeksi Relasional PostgreSQL Asli)
                            // Menyimpan Mahasiswa
                            const dbId = await this.dbAdapter.upsertStudent(
                                studentId, 
                                fullName,
                                angkatan, 
                                finalProdi, 
                                studentObj.academic_status
                            );
                            
                            // Integrasi PA: Pasangkan relasi pembimbing
                            if (advisorMap[studentId]) {
                                await this.dbAdapter.assignAdvisor(studentId, advisorMap[studentId]);
                            }
                            
                            // Asumsikan data didampingi oleh metrik dari webhook
                            if (transcript) {
                                const normalizedTranscripts = this.dataNormalizer.normalizeTranscript(transcript);
                                let totalCredits = 0;
                                let totalBobot = 0;
                                
                                for (const t of normalizedTranscripts) {
                                    const courseDbId = await this.dbAdapter.upsertCourse(t.course_code, t.course_name, t.credits, t.semester);
                                    await this.dbAdapter.upsertGrade(dbId, courseDbId, t.semester, t.grade_letter, t.grade_weight);
                                    
                                    totalCredits += t.credits;
                                    totalBobot += (t.grade_weight * t.credits);
                                }
                                
                                const ipk = totalCredits > 0 ? (totalBobot / totalCredits).toFixed(2) : 0;
                                await this.dbAdapter.upsertAcademicRecord(dbId, ipk, totalCredits);
                            } else {
                                // Fallback: Inject Basic Academic Record if Transcript API Drops
                                await this.dbAdapter.upsertAcademicRecord(
                                    dbId, 
                                    studentObj.cumulative_gpa || 0, 
                                    studentObj.total_credits || 0
                                );
                            }
                            
                            this.audit.log(account.id, 'DB Sync', 'SUCCESS', `Disisipkan ke DB AIMS: ${studentId} (Record ID: ${dbId})`);
                        }, async (studentObj) => {
                            const studentId = studentObj.student_id;
                            if (!studentId || !studentId.toUpperCase().startsWith('F')) return;
                            
                            let finalProdi = null;
                            if (studentObj.raw_prodi) {
                                const raw = studentObj.raw_prodi.toUpperCase();
                                if (raw.includes('MANDARIN')) {
                                    finalProdi = 'Bahasa Mandarin & kebudayaan Tiongkok';
                                } else {
                                    finalProdi = FIB_PRODI_MAP[raw];
                                }
                            }
                            
                            // Dynamic fallback for S2/S3 based on NIM prefixes
                            if (!finalProdi && studentId) {
                                const idUpper = studentId.toUpperCase();
                                if (idUpper.startsWith('F062')) finalProdi = 'Kajian Budaya (S2)';
                                else if (idUpper.startsWith('F032')) finalProdi = 'Bahasa Indonesia (S2)';
                                else if (idUpper.startsWith('F013')) finalProdi = 'Ilmu Linguistik (S3)';
                                else if (idUpper.startsWith('F042')) finalProdi = 'Arkeologi (S2)';
                                else if (idUpper.startsWith('F022')) finalProdi = 'Bahasa Inggris (S2)';
                                else if (idUpper.startsWith('F012')) finalProdi = 'Linguistik (S2)';
                                else if (idUpper.startsWith('F033')) finalProdi = 'Sastra Indonesia (S3)';
                                else if (idUpper.startsWith('F052')) finalProdi = 'Sejarah (S2)';
                                else if (idUpper.startsWith('F023')) finalProdi = 'Bahasa Inggris (S3)';
                            }
                            
                            if (!finalProdi) return; // Drop
                            
                            const dbId = await this.dbAdapter.upsertStudent(studentId, studentObj.full_name || ("Mahasiswa " + studentId), angkatan, finalProdi, studentObj.academic_status);
                            await this.dbAdapter.upsertAcademicRecord(
                                dbId, 
                                studentObj.cumulative_gpa || 0, 
                                studentObj.total_credits || 0
                            );
                        }, null, nimsWithGrades);
                        totalSynced += syncReport.syncedCount;
                    }
                }

                this.audit.log(account.id, 'Sync Completed', 'SUCCESS', `Delta Sync Finished. Total Mutated: ${totalSynced}`);
            } catch (e) {
                this.audit.log(account.id, 'Sync', 'FAILED', e.message);
                throw e; 
            }
        });
    }
}
