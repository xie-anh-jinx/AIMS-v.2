import urllib.request
import json

with open("/root/AIMS/.env", "r") as f:
    token = ""
    for line in f:
        if line.startswith("NEOSIA_TOKEN="):
            token = line.strip().split("=", 1)[1]
            token = token.strip('"').strip("'")
            break

url = "https://api.neosia.unhas.ac.id/api/admin/penasihat_akademik"
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
try:
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')
        js = json.loads(data)
        print("Status: 200")
        print("Keys:", js.keys())
        if 'data' in js: print("Data length:", len(js['data']))
        if 'dosens' in js: print("Dosens length:", len(js['dosens']))
except Exception as e:
    print(f"Error: {e}")
