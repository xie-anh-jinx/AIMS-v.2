import json
from collections import defaultdict

file_path = "plugins/academic-connector/pa_dump_all.json"
with open(file_path, "r") as f:
    data = json.load(f)

# Maps student NIM to a list of tuples: (pa_nip, pa_name)
student_to_pas = defaultdict(list)

# Track how many PAs are completely empty after final override
pa_initial_counts = defaultdict(int)
pa_final_counts = defaultdict(int)
pa_names = {}

for paObj in data:
    d = paObj.get("dosen") or paObj
    nip = str(d.get("nip") or d.get("id_pegawai") or d.get("username") or "")
    if not nip: continue
    
    nama = d.get("nama_dosen") or d.get("nama") or f"Dosen {nip}"
    pa_names[nip] = nama
    
    mhs_list = paObj.get("mahasiswas") or paObj.get("bimbingan") or []
    for mhs in mhs_list:
        nim_mhs = str(mhs if isinstance(mhs, str) else (mhs.get("nim") or mhs.get("id") or ""))
        if nim_mhs:
            student_to_pas[nim_mhs].append((nip, nama))
            pa_initial_counts[nip] += 1

# Calculate final counts based on "last one wins" logic
for nim, pas in student_to_pas.items():
    if not pas: continue
    last_pa_nip = pas[-1][0]
    pa_final_counts[last_pa_nip] += 1

# Analyze losers (PAs who had >0 initial but 0 final or lost significant amount)
total_stolen = 0
stolen_students_count = 0
for nim, pas in student_to_pas.items():
    if len(pas) > 1:
        stolen_students_count += 1

print(f"Total students mapped: {len(student_to_pas)}")
print(f"Total students assigned to MULTIPLE PAs: {stolen_students_count}")

completely_lost_pas = []
for nip, count in pa_initial_counts.items():
    if count > 0 and pa_final_counts[nip] == 0:
        completely_lost_pas.append(pa_names[nip])

print(f"\nNumber of PAs whose entire student list was stolen: {len(completely_lost_pas)}")
if completely_lost_pas:
    print("Example PAs totally emptied:", completely_lost_pas[:5])

# Print some duplicate examples
print("\nExamples of stolen students:")
examples = 0
for nim, pas in student_to_pas.items():
    if len(pas) > 1:
        # Get unique PAs for this student
        unique_pas = list({p[0]: p for p in pas}.values())
        if len(unique_pas) > 1:
            print(f"Student {nim} was claimed by:")
            for p in unique_pas:
                print(f"  - {p[1]} ({p[0]})")
            examples += 1
            if examples >= 5: break
