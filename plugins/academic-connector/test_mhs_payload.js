import fs from 'fs';
import fetch from 'node-fetch';
import { AcademicConnector } from './src/AcademicConnector.js';

const tok = JSON.parse(fs.readFileSync('./providers/fib_superadmin/session.json')).bearerToken;
const connector = new AcademicConnector();
connector.restAdapter.baseUrl = 'https://api.neosia.unhas.ac.id';

async function test() {
    const data = await connector.restAdapter.get('https://api.neosia.unhas.ac.id/api/admin/penasihat_akademik?filters[id_prodi_semester]=996', { bearerToken: tok });
    const paArray = data.dosens || data.penasihat_akademiks || data.data || [];
    for(const p of paArray) {
        if(p.mahasiswas && p.mahasiswas.length > 0) {
            console.log("Mahasiswa Object format:");
            console.log(p.mahasiswas[0]);
            process.exit(0);
        }
    }
}
test();
