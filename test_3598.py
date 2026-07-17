import urllib.request
import json
with open("/root/AIMS/.env", "r") as f:
    token = [line.strip().split("=", 1)[1].strip('"').strip("'") for line in f if line.startswith("NEOSIA_TOKEN=")][0]

url = "https://api.neosia.unhas.ac.id/api/admin/penasihat_akademik?filters[id_prodi_semester]=3598"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
with urllib.request.urlopen(req) as response:
    js = json.loads(response.read().decode('utf-8'))
    print("Maha count:", sum(len(d.get('mahasiswas', [])) for d in js.get('dosens', [])))
