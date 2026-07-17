import json, urllib.request, os

token = os.environ.get("NEOSIA_TOKEN")
req = urllib.request.Request("https://api.neosia.unhas.ac.id/api/admin/transkrip/getTranskripMahasiswa?nim=F021191049")
req.add_header("Authorization", f"Bearer {token}")
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        print("current_indeks_prestasi:", data.get("current_indeks_prestasi"))
        transkrips = data.get("transkrips", [])
        valid_sks = sum(t.get("sks", 0) for t in transkrips if t.get("is_used") == 1)
        weighted_sum = sum(t.get("sks", 0) * float(t.get("nilai_angka") or 0.0) for t in transkrips if t.get("is_used") == 1)
        ipk_est = (weighted_sum / valid_sks) if valid_sks > 0 else 0
        print(f"Total SKS (is_used=1): {valid_sks}, IPK Estimasi: {ipk_est:.2f}")
except Exception as e:
    print(f"Error: {e}")
