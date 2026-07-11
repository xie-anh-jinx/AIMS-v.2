import fetch from 'node-fetch';
async function run() {
    const url = 'https://api.neosia.unhas.ac.id/api/admin/penasihat_akademik?filters[id_prodi_semester]=3600';
    try {
        const res = await fetch(url);
        console.log("TEXT DUMP:", await res.text());
    } catch(e) { console.error(e) }
}
run();
