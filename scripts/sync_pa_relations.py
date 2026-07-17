import os
import urllib.request
import json
import difflib
import time
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from typing import List

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://aims_user:aims_password@localhost:5435/aims_db")
engine = create_engine(DATABASE_URL)

with open("/root/AIMS/.env", "r") as f:
    token = ""
    for line in f:
        if line.startswith("NEOSIA_TOKEN="):
            token = line.strip().split("=", 1)[1]
            token = token.strip('"').strip("'")
            break

def fetch_json(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetcing {url} : {e}")
        return None

print("Menyelaraskan Relasi Penasihat Akademik (PA)...")

with engine.connect() as conn:
    res = conn.execute(text("SELECT id, nim, prodi FROM students")).mappings().all()
    nim_to_id = {row['nim']: row['id'] for row in res}
    nim_to_prodi = {row['nim']: row['prodi'] for row in res}
    
    res = conn.execute(text("SELECT id, nama, prodi FROM advisors")).mappings().all()
    advisors = [{'id': r['id'], 'nama': r['nama'], 'prodi': r['prodi']} for r in res]
    
    def match_advisor(neosia_name, advisors):
        neo = neosia_name.lower().replace('.', '').replace(',', '')
        best_match = None
        highest_ratio = 0.0
        for adv in advisors:
            db_name = adv['nama'].lower().replace('.', '').replace(',', '')
            ratio = difflib.SequenceMatcher(None, neo, db_name).ratio()
            if db_name in neo or neo in db_name:
                ratio += 0.3
            if ratio > 0.75 and ratio > highest_ratio:
                highest_ratio = ratio
                best_match = adv['id']
        return best_match

    found_ps_ids = []
    print("Mencari ID Prodi Semester aktif dari API prodi id 20-50...")
    for i in range(20, 50): # Limiting ranges to common UNHAS FIB IDs to avoid 30req/min ratelimit
        url = f"https://api.neosia.unhas.ac.id/api/admin/prodi_semester?filters[id_prodi]={i}&filters[is_used]=1"
        data = fetch_json(url)
        if data and 'prodiSemesters' in data:
            for ps in data['prodiSemesters']:
                if ps.get('is_active') == 1:
                    found_ps_ids.append(ps['id'])
                    break
        time.sleep(2) # RATELIMIT Wait

    print(f"Ditemukan {len(found_ps_ids)} id_prodi_semester aktif.")
    
    total_assigned = 0
    for ps_id in found_ps_ids:
        print(f"-> Sync ID Semester: {ps_id}...")
        url = f"https://api.neosia.unhas.ac.id/api/admin/penasihat_akademik?filters[id_prodi_semester]={ps_id}"
        js = fetch_json(url)
        time.sleep(2)
        if not js or 'dosens' not in js:
            continue
            
        for d in js['dosens']:
            if not d.get('dosen'):
                continue
            neo_dosen_nama = d['dosen']['nama']
            adv_id = match_advisor(neo_dosen_nama, advisors)
            if not adv_id:
                continue 
                
            prodi_string = None
            mahasiswas = d.get('mahasiswas', [])
            nim_list = [m['nim'] for m in mahasiswas if m['nim'] in nim_to_id]
            
            if not nim_list:
                continue

            counts = {}
            for n in nim_list:
                p = nim_to_prodi[n]
                if p: counts[p] = counts.get(p, 0) + 1
            if counts:
                prodi_string = max(counts, key=counts.get)
            
            total_assigned += len(nim_list)
            
            if prodi_string:
                conn.execute(
                    text("UPDATE advisors SET prodi = :prodi WHERE id = :id"),
                    {"prodi": prodi_string, "id": adv_id}
                )
                
            if nim_list:
                # chunking updates for students
                for nim in nim_list:
                    conn.execute(
                        text("UPDATE students SET advisor_id = :ad_id WHERE nim = :nim"),
                        {"ad_id": adv_id, "nim": nim}
                    )
        conn.commit()

print(f"\\nProses Sinkronisasi Relasi Selesai! Berhasil mengikat {total_assigned} relasi Mahasiswa-Dosen.")
