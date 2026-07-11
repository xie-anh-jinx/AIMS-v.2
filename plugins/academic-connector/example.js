import * as dotenv from 'dotenv';
dotenv.config();

import { AcademicConnector } from './src/AcademicConnector.js';

async function main() {
    console.log("=== Membuka Gerbang Enterprise Data SDK (Multi-Account V3) ===");
    
    // Inisialisasi Orchestrator V3
    const sdk = new AcademicConnector();
    
    try {
        // Pendelegasian 10 akun Prodi sekaligus! (Scheduler Ingestion)
        await sdk.executeMultiAccountSync();
        console.log("\n=== Laporan Delta Sync V3 Selesai ===");
    } catch (error) {
        console.error(`⛔ Terjadi Galat Kritis pada Level Engine: ${error.message}`);
    } finally {
        sdk.logger.flush('v3-hybrid.log');
    }
}

main();
