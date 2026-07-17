import urllib.request
import json
with open("/root/AIMS/.env", "r") as f:
    token = [line.strip().split("=", 1)[1].strip('"').strip("'") for line in f if line.startswith("NEOSIA_TOKEN=")][0]

url = "https://api.neosia.unhas.ac.id/api/admin/prodi_semester?filters[id_prodi]=33&filters[is_used]=1"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
with urllib.request.urlopen(req) as response:
    js = json.loads(response.read().decode('utf-8'))
    print(json.dumps(js)[:1500])
