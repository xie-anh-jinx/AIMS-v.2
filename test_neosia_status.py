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

def get_student_neosia_status(nim: str, prodi_name: str, angkatan: int):
    # 1. Resolve id_prodi and id_prodi_semester
    with httpx.Client(timeout=15) as client:
        # Standardize matching name
        std_prodi = prodi_name.upper().strip()
        # Some DB prodi may not have "- S1", let's handle that, e.g. "SASTRA PRANCIS" -> "SASTRA PRANCIS - S1"
        if not std_prodi.endswith("- S1") and not std_prodi.endswith("- S2") and not std_prodi.endswith("- S3"):
            std_prodi = f"{std_prodi} - S1"

        url_ps = f"{NEOSIA_API_BASE}/api/admin/prodi_semester?filters[is_used]=1"
        r_ps = client.get(url_ps, headers=HEADERS)
        if r_ps.status_code != 200:
            return {"error": "Failed to fetch prodi semesters", "code": r_ps.status_code}
        
        ps_arr = r_ps.json().get("prodiSemesters") or r_ps.json().get("data") or []
        
        matched_ps = None
        for ps in ps_arr:
            p_name = (ps.get("prodi") or {}).get("nama_resmi", "").upper()
            if std_prodi in p_name or p_name in std_prodi:
                matched_ps = ps
                break
        
        if not matched_ps:
            # Fallback: look for partial match
            for ps in ps_arr:
                p_name = (ps.get("prodi") or {}).get("nama_resmi", "").upper()
                if any(w in p_name for w in std_prodi.split() if len(w) > 3):
                    matched_ps = ps
                    break

        if not matched_ps:
            return {"error": f"Prodi '{prodi_name}' not found in active semesters"}

        id_prodi = matched_ps["id_prodi"]
        id_prodi_semester = matched_ps["id"]
        sem_year = matched_ps.get("semester", {}).get("tahun_ajaran")
        sem_term = matched_ps.get("semester", {}).get("jenis")
        
        print(f"Matched Prodi: {matched_ps['prodi']['nama_resmi']} (id_prodi={id_prodi}, id_prodi_semester={id_prodi_semester})")

        # 2. Query status_krs
        url_krs = f"{NEOSIA_API_BASE}/api/admin/mahasiswa/status_krs?filters[id_prodi]={id_prodi}&filters[angkatan]={angkatan}&filters[id_prodi_semester]={id_prodi_semester}"
        r_krs = client.get(url_krs, headers=HEADERS)
        if r_krs.status_code != 200:
            return {"error": "Failed to fetch status_krs", "code": r_krs.status_code}

        krs_data = r_krs.json()
        mahasiswas = krs_data.get("mahasiswas", {})
        
        sudah_krs = mahasiswas.get("sudah_krs", [])
        belum_krs = mahasiswas.get("belum_krs", [])
        
        target_nim = nim.upper().strip()
        found_mhs = None
        status_krs = "BELUM_KRS"
        
        for m in sudah_krs:
            m_info = m.get("mahasiswa") or m
            if str(m_info.get("nim", "")).upper().strip() == target_nim:
                found_mhs = m_info
                status_krs = "SUDAH_KRS"
                break
                
        if not found_mhs:
            for m in belum_krs:
                m_info = m.get("mahasiswa") or m
                if str(m_info.get("nim", "")).upper().strip() == target_nim:
                    found_mhs = m_info
                    status_krs = "BELUM_KRS"
                    break
                    
        if not found_mhs:
            return {"error": f"Student with NIM {nim} not found in this prodi's KRS records", "id_prodi": id_prodi, "id_prodi_semester": id_prodi_semester}

        # 3. Extract payment status
        pay_info = found_mhs.get("statusPembayaran") or {}
        sudah_bayar = pay_info.get("sudah_bayar") == 1
        nominal = pay_info.get("nominal") or found_mhs.get("spp")
        
        return {
            "nim": target_nim,
            "nama": found_mhs.get("nama_mahasiswa"),
            "status_krs": status_krs,
            "sudah_bayar": sudah_bayar,
            "nominal_spp": nominal,
            "tahun_ajaran": sem_year,
            "semester_jenis": sem_term
        }

# Test for F051221022 (VICTORIA)
print(get_student_neosia_status("F051221022", "Sastra Prancis", 2022))
