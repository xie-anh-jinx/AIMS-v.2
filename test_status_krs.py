import os
import httpx
from dotenv import load_dotenv

load_dotenv(".env")
NEOSIA_API_BASE = os.getenv("NEOSIA_API_BASE", "https://api.neosia.unhas.ac.id")
NEOSIA_TOKEN = os.getenv("NEOSIA_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {NEOSIA_TOKEN}",
    "Accept": "application/json"
}

with httpx.Client(timeout=15) as client:
    # Query prodiSemesters
    url_ps = f"{NEOSIA_API_BASE}/api/admin/prodi_semester?filters[is_used]=1"
    r_ps = client.get(url_ps, headers=HEADERS)
    if r_ps.status_code == 200:
        data = r_ps.json()
        ps_arr = data.get("prodiSemesters") or data.get("data") or []
        print(f"Total prodi semesters: {len(ps_arr)}")
        if ps_arr:
            print("First item in prodi semesters:")
            import pprint
            pprint.pprint(ps_arr[0])
            # Check unique prodi names/ids
            prodi_info = []
            for ps in ps_arr:
                prodi = ps.get("prodi") or {}
                sem = ps.get("semester") or {}
                prodi_info.append({
                    "id_prodi_semester": ps.get("id") or ps.get("id_prodi_semester"),
                    "id_prodi": prodi.get("id"),
                    "prodi_name": prodi.get("nama_resmi"),
                    "semester_tahun": sem.get("tahun"),
                    "semester_jenis": sem.get("jenis")
                })
            print("\nList of prodi names and mapped IDs:")
            pprint.pprint(prodi_info[:20])
