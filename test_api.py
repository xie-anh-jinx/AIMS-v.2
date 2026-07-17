import urllib.request
import json
import base64

with open("/root/AIMS/.env", "r") as f:
    token = ""
    for line in f:
        if line.startswith("NEOSIA_TOKEN="):
            token = line.strip().split("=", 1)[1]
            token = token.strip('"').strip("'")
            break

url = "https://api.neosia.unhas.ac.id/api/admin/penasihat_akademik?filters[id_prodi_semester]=3598"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
try:
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')
        js = json.loads(data)
        print("Status: 200")
        print(json.dumps(js)[:1500])
except Exception as e:
    print(f"Error: {e}")
