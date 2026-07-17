import urllib.request
import json

with open("/root/AIMS/.env", "r") as f:
    token = ""
    for line in f:
        if line.startswith("NEOSIA_TOKEN="):
            token = line.strip().split("=", 1)[1]
            token = token.strip('"').strip("'")
            break

valid_ids = []
for i in range(3590, 3610):
    url = f"https://api.neosia.unhas.ac.id/api/admin/penasihat_akademik?filters[id_prodi_semester]={i}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if 'dosens' in data and len(data['dosens']) > 0:
                print(f"Found valid ID {i}: {data['dosens'][0]['dosen']['nama']} - {data['dosens'][0]['mahasiswas'][0]['prodi']['nama_resmi']}")
                valid_ids.append(i)
    except:
        pass
print("Validated:", valid_ids)
