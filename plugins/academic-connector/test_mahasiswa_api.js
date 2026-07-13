import fs from 'fs';
import { AcademicConnector } from './src/AcademicConnector.js';

async function testApi() {
    const tokFile = './providers/fib_superadmin/session.json';
    if (!fs.existsSync(tokFile)) { console.log('No token'); return; }
    const tok = JSON.parse(fs.readFileSync(tokFile)).bearerToken;

    const connector = new AcademicConnector();
    connector.restAdapter.baseUrl = 'https://api.neosia.unhas.ac.id';
    
    // Let's try hitting a generic mahasiswa endpoint if it exists
    const endpoints = [
        'https://api.neosia.unhas.ac.id/api/admin/mahasiswa?limit=5',
        'https://api.neosia.unhas.ac.id/api/admin/rekap_ipk?limit=5',
        'https://api.neosia.unhas.ac.id/api/admin/mahasiswa_aktif?limit=5',
    ];

    for (let ep of endpoints) {
        console.log(`Trying ${ep}...`);
        try {
            const data = await connector.restAdapter.get(ep, { bearerToken: tok });
            console.log(`SUCCESS on ${ep}! Key keys:`, Object.keys(data));
            if (data.data && Array.isArray(data.data) && data.data.length > 0) {
                console.log(`Sample obj keys:`, Object.keys(data.data[0]));
                if (data.data[0].ipk || data.data[0].ipk_estimasi) {
                    console.log("FOUND IPK BUKTINYA BISA!");
                }
            } else if (Array.isArray(data) && data.length > 0) {
                console.log(`Sample obj keys:`, Object.keys(data[0]));
            }
        } catch (e) {
            console.log(`FAILED ${ep} -> ${e.response?.status || e.message}`);
        }
    }
}
testApi();
