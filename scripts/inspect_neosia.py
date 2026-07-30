import httpx
import json

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIyIiwianRpIjoiMDZjZTI3ZjAzYzUxOWZiNzk5ZjdlZTVlMzdjNzg0MGRjMmUwOWNmZjFkYjBiM2ZlNTNiOGVjZmFlNGM1NWEyZmZkYzUzYjc1ODNjZGU3MGIiLCJpYXQiOjE3ODQ5NzkxNDMuNjYzNDEyLCJuYmYiOjE3ODQ5NzkxNDMuNjYzNDE1LCJleHAiOjE3ODU0MTExNDMuNjU3MzQ1LCJzdWIiOiI4ODQyNSIsInNjb3BlcyI6WyIqIl19.BJJwWCpsw0ZLqTVtqvdy6ZyeTTbN3aYFbjr6D_ukeT0zjNjm5E0f0AJe8Y9lfAV9PwM-KxMCW6xvKWC0J-LxTZ99pWWGhMqDIAYbR1paj3KN5ggEtWYo0upZ1X8J9-kEk5CK2HaC9oRWCSjtV-QgfXW_SdEQi4aa68pevF1rMJlgsXBCqKKTnFYDn48Lb6NILBHnxgVbrBpIoGH3wZQOMegDwG-9zHXXLJyO0oi_uV2PmZPH_ovyOB3mHj7pohX0ZybHhkT_71QvYKnieW-Pzra7uwv_Aaet0V2jmDj6PSX6fGjZy-ihmoqIWcd2KDD18tfqldd0hRLmxYzKtzfOOBUP2GlfFiDVH71BnRLbN7zKaJUkIty-yN5f_CGGjaM75VleKNZ4nvJLA3XKg-_RVbjttvxoGV8i02q6wQbyhypK_HkfSFB6Acelcisl7-GohTghmXc7sBkzUblY6Oeu09zGn54XrVjFaQ0wLLplbzH2j3_qE8jqd-E7wYu93TRyctHrbsJApVILVefwpeBGVhtbkxVWRNR0P7iAaFlnNc_0fai7-j3SL6BD8VDUdfvCSwKYRyKqnsNeZiGrNbLnOeyA8c6hdugn_p-_AjlYSb4eSIJoJKDz3TV8cK6M7I7-QchdvYEeGBMKbjWd2RYcXQbatocb_9AdXELBEQ7-cy0"
headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
NEOSIA_BASE = "https://api.neosia.unhas.ac.id"

res = httpx.get(f"{NEOSIA_BASE}/api/admin/prodi", headers=headers, timeout=15)
if res.status_code == 200:
    data = res.json()
    if "prodis" in data:
        for p in data["prodis"]:
            fak = p.get('fakultas', {}) or {}
            fak_name = fak.get('nama_resmi', '') if isinstance(fak, dict) else ''
            p_name = p.get("nama_resmi", "")
            if "SEJARAH" in p_name or "ARKEOLOGI" in p_name or "MANDARIN" in p_name:
                print(p.get('id'), p.get('nama_resmi'), fak_name)
