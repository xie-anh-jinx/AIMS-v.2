import os
import bcrypt
from packages.database.connection import SessionLocal
from packages.database.models import Student, Advisor, User

db = SessionLocal()

hashed = bcrypt.hashpw(b"password123", bcrypt.gensalt(rounds=12)).decode("utf-8")
linked = 0
not_found_students = []

raw_data = """F051201018	2020	ALFINA MUTHMAINNAH	Prof. Dr. Muhammad Hasyim, M.Si.
F051201020	2020	AHMAD BAIHAQI	Prof. Dr. Muhammad Hasyim, M.Si.
F051221007	2022	BUCEK ALEXSANDER .C. ROHI KORE	Prof. Dr. Muhammad Hasyim, M.Si.
F051221009	2022	OLIVIA PUTRI BINTOEN	Prof. Dr. Muhammad Hasyim, M.Si.
F051221020	2022	INGGRID PATMA MANGAMBU	Prof. Dr. Muhammad Hasyim, M.Si.
F051221021	2022	NABILA DWI AZIRA AINUN	Prof. Dr. Muhammad Hasyim, M.Si.
F051231036	2023	AURA AZ ZAHRA ASRUL	Prof. Dr. Muhammad Hasyim, M.Si.
F051231057	2023	MUHAMMAD AULIA FAIQ	Prof. Dr. Muhammad Hasyim, M.Si.
F051221017	2022	RISKY AMELIA BURHAN	Prof. Dr. Muhammad Hasyim, M.Si.
F051221030	2022	SITI NUR AISYAH	Prof. Dr. Muhammad Hasyim, M.Si.
F051251013	2025	NADYA PRATIWI	Drs. Hasbullah, M.Hum.
F051251024	2025	DESY ANGRAENI PUSPITA AYU	Drs. Hasbullah, M.Hum.
F051211002	2021	ZUL FAHMI KUM	Drs. Hasbullah, M.Hum.
F051221010	2022	NINING FARADIBA	Drs. Hasbullah, M.Hum.
F051221012	2022	ANUGRAH YEMIMA LEMBAYUNG	Drs. Hasbullah, M.Hum.
F051221019	2022	SYAZWINA ALIFA BOWASIS UMAR	Drs. Hasbullah, M.Hum.
F051221025	2022	AMELIA PINKAN SAVITRI	Drs. Hasbullah, M.Hum.
F051221028	2022	ANUGRAH PUTRA PRASETYA	Drs. Hasbullah, M.Hum.
F051221033	2022	AURIL JASMIN ADFAHIRA	Drs. Hasbullah, M.Hum.
F051221040	2022	FAUZTINA ARIANISAH	Drs. Hasbullah, M.Hum.
F051221041	2022	AUFA ZAVIERA ASHEZAH	Drs. Hasbullah, M.Hum.
F051221042	2022	M. ISMAIL IRGI HARUNA	Drs. Hasbullah, M.Hum.
F051221046	2022	DIAN RISA FEBRIANI	Drs. Hasbullah, M.Hum.
F051251029	2025	MUH. RIFQI ZACKY ASHAR	Dra. Irianty Bandu, M.Pd
F051251037	2025	CAISAH IRVAN	Dra. Irianty Bandu, M.Pd
F051231002	2023	MUHAMMAD PARMAN SAPUTRA REZA	Dra. Irianty Bandu, M.Pd
F051231008	2023	AVRIL FAITH NICOLE LINTANG	Dra. Irianty Bandu, M.Pd
F051231038	2023	MUH.RYAAS WIRAHADIKUSUMA SYARIEF	Dra. Irianty Bandu, M.Pd
F051231052	2023	FATHIR KAMAL FADHILLA CHANIAGO	Dra. Irianty Bandu, M.Pd
F051231062	2023	MUHAMMAD DZIKIR ZAINUL MUTTAQIN	Dra. Irianty Bandu, M.Pd
F051251036	2025	ARIQAH QANITAH ANDARI NARRA	Dr. Wahyuddin, SS., M.Hum.
F051251008	2025	MUHAMMAD ASIAN	Dr. Wahyuddin, SS., M.Hum.
F051251001	2025	NAYSHIVA NASRIAH MARLIN	Dr. Wahyuddin, SS., M.Hum.
F051201010	2020	MIRAJ MUHAMMAD	Dr. Wahyuddin, SS., M.Hum.
F051241001	2024	ANNISA AURELLIA RAMADHANI ERWIN	Dr. Wahyuddin, SS., M.Hum.
F051241044	2024	ASMAR RAIHAN	Dr. Wahyuddin, SS., M.Hum.
F051241034	2024	NAURAH ABIFA	Dr. Wahyuddin, SS., M.Hum.
F051241043	2024	ANYA NUR ZAKIYYAH	Dr. Wahyuddin, SS., M.Hum.
F051241069	2024	INTANG	Dr. Wahyuddin, SS., M.Hum.
F051241020	2024	HUSNUL CHOTIMAH	Dr. Wahyuddin, SS., M.Hum.
F051241072	2024	RANDI AWALIA RAMADHAN	Dr. Wahyuddin, SS., M.Hum.
F051241022	2024	DAVINA FATIN	Dr. Wahyuddin, SS., M.Hum.
F051201022	2020	MAHARANI	Dr. Wahyuddin, SS., M.Hum.
F051251002	2025	JUNICA MARSYALINDA J.	Dr. Andi Faisal, S.S.,M.Hum.
F051251004	2025	AYUDIA DWI KIRANA	Dr. Andi Faisal, S.S.,M.Hum.
F051251006	2025	SITI QANITAH DEAPATI	Dr. Andi Faisal, S.S.,M.Hum.
F051251009	2025	DIAN TANDI	Dr. Andi Faisal, S.S.,M.Hum.
F051231010	2023	DELA PUSPITA SARI	Dr. Andi Faisal, S.S.,M.Hum.
F051231047	2023	PUTRI	Dr. Andi Faisal, S.S.,M.Hum.
F051221005	2022	NUR ASIAH	Dr. Andi Faisal, S.S.,M.Hum.
F051191010	2019	Tarika Febrina Ayunani	Dr. Andi Faisal, S.S.,M.Hum.
F051211014	2021	HELMA SRI JULIANA	Dr. Andi Faisal, S.S.,M.Hum.
F051231012	2023	NURWAN	Dr. Andi Faisal, S.S.,M.Hum.
F051231013	2023	A. RATU DEWI RAMADANI	Dr. Andi Faisal, S.S.,M.Hum.
F051231014	2023	NURZAHRA INKANASYAH M	Dr. Andi Faisal, S.S.,M.Hum.
F051231016	2023	ANINDYA NYNA LESTARI	Dr. Andi Faisal, S.S.,M.Hum.
F051231017	2023	STEPHEN TIMOTHY HAMONANGAN GULTOM	Dr. Andi Faisal, S.S.,M.Hum.
F051231023	2023	ST. FATHIREZKY AULIA MAHARANI	Dr. Andi Faisal, S.S.,M.Hum.
F051231043	2023	KASMA WATI	Dr. Andi Faisal, S.S.,M.Hum.
F051211023	2021	ANUGRAH SRI ASTUTI JUWITA S.	Dr. Andi Faisal, S.S.,M.Hum.
F051211005	2021	MARDAYANTI M	Dr. Andi Faisal, S.S.,M.Hum.
F051251011	2025	ANDI NABIL AL ARSY	Masdiana, SS.,M.Hum.
F051251044	2025	MARSYA MUZZADYA	Masdiana, SS.,M.Hum.
F051251003	2025	MUHAMMAD FATIHATUL RIZQY	Masdiana, SS.,M.Hum.
F051251005	2025	SYERINA SYAHRAH	Masdiana, SS.,M.Hum.
F051231024	2023	RISWANDA	Masdiana, SS.,M.Hum.
F051231009	2023	DAVINA ILMALIA PUTRI	Masdiana, SS.,M.Hum.
F051221001	2022	ASPAYANI PARUPANG	Masdiana, SS.,M.Hum.
F051221002	2022	ANDI DEEVA KEIKO WIRAPUTRI	Masdiana, SS.,M.Hum.
F051221003	2022	SAMANTHA AZURA SALSABILLA	Masdiana, SS.,M.Hum.
F051221026	2022	MARIA ANGELIQA RIEKE TANEH	Masdiana, SS.,M.Hum.
F051221037	2022	PUTRI WAHYU MAHARANI	Masdiana, SS.,M.Hum.
F051221043	2022	NUR HANDAYANI	Masdiana, SS.,M.Hum.
F051241060	2024	FARAH JASMINE SASABONE	Masdiana, SS.,M.Hum.
F051241047	2024	YAHDIT MULYADI	Masdiana, SS.,M.Hum.
F051241037	2024	BESSE RAHMA ALSA	Masdiana, SS.,M.Hum.
F051221014	2022	NISRINA RAHMA MAULIDA	Masdiana, SS.,M.Hum.
F051251021	2025	AFIFAH NURANIYYAH ARMAN	Masdiana, SS.,M.Hum.
F051231005	2023	ATHIYAH DHAWY KHALISHAH	Dr. Prasuri Kuswarini, MA.
F051231004	2023	MUH. SYAIFULLAH KHOMEINI	Dr. Prasuri Kuswarini, MA.
F051241010	2024	RIFQI FACHRI	Dr. Prasuri Kuswarini, MA.
F051241027	2024	A.HIJRATUL ASYIFA	Dr. Prasuri Kuswarini, MA.
F051241042	2024	SALSABILA	Dr. Prasuri Kuswarini, MA.
F051241061	2024	SALPA	Dr. Prasuri Kuswarini, MA.
F051241065	2024	SITI DARI WULAN	Dr. Prasuri Kuswarini, MA.
F051241074	2024	VERA SINTIA	Dr. Prasuri Kuswarini, MA.
F051241005	2024	INSEREN NUMFOR R. MORIN	Dr. Prasuri Kuswarini, MA.
F051191049	2019	Risma I.H	Dr. Prasuri Kuswarini, MA.
F051211031	2021	PUTRI OKTOVIANI	Dr. Prasuri Kuswarini, MA.
F051221006	2022	GIBRAN SYACH FATAHILLAH	Dr. Prasuri Kuswarini, MA.
F051221024	2022	DIANDITA SHASIKIRANA PUTRI SOEHARTO	Dr. Prasuri Kuswarini, MA.
F051231021	2023	DELLA SARI	Dr. Prasuri Kuswarini, MA.
F051231028	2023	PUAN LAIKA RANDY	Dr. Prasuri Kuswarini, MA.
F051241018	2024	DANDELION CORLEONE ANDI KARIM	Dr. Prasuri Kuswarini, MA.
F051251007	2025	MUHAMMAD IMRAN KADIR	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051251010	2025	NANDA KHALILAH QUINTA PUTRI	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051251012	2025	A. NARAYA NURHADI INDHINHY	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051211037	2021	RENALDI JUPRI	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051231006	2023	NABILA NUR RIDZKY SUREDA	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051231049	2023	YUNITA SALIUS	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051221011	2022	M. SYAIRIL ADZEHAR IBRAHIM	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051221022	2022	VICTORIA APRILIA PUTRI	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051221029	2022	AMYRAH NABILAH RIDWAN	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051221032	2022	ZELDA LAWRENT PETRINA LEWI	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051221036	2022	NINING WIDYANINGSIH	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051231042	2023	TIARA SIKOMBONG	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051231044	2023	NURUL ANITA	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051231046	2023	EKA PASUBA'	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051191055	2019	A. Alief Ahdab	Dr. Fierenziana Getruida Junus, SS.,M.Hum.
F051251014	2025	FAULIN RAMBA	Dr. Ade Yolanda Latjuba, SS.,MA.
F051251015	2025	ROWY AFGA ANUGRAH	Dr. Ade Yolanda Latjuba, SS.,MA.
F051251016	2025	KHAISYAH SYARAFAH AL PITRAH	Dr. Ade Yolanda Latjuba, SS.,MA.
F051231001	2023	NURUL RAMADHANI AULIA	Dr. Ade Yolanda Latjuba, SS.,MA.
F051231007	2023	ALIFIA AZHARANI PUTRI R.	Dr. Ade Yolanda Latjuba, SS.,MA.
F051231019	2023	ANISA MARIFFYA SETIAWAN	Dr. Ade Yolanda Latjuba, SS.,MA.
F051211028	2021	AHMAD ARIFIN	Dr. Ade Yolanda Latjuba, SS.,MA.
F051211050	2021	MUHAMMAD ISAL	Dr. Ade Yolanda Latjuba, SS.,MA.
F051221008	2022	SITTI AISYAH	Dr. Ade Yolanda Latjuba, SS.,MA.
F051221027	2022	SITI SUNDARI ABDULLAH	Dr. Ade Yolanda Latjuba, SS.,MA.
F051221045	2022	PINTAR NABILA ZAINAL	Dr. Ade Yolanda Latjuba, SS.,MA.
F051231040	2023	NAJWA ULAIYA SAFITRI	Dr. Ade Yolanda Latjuba, SS.,MA.
F051231048	2023	ABHIGAEL PATRICIA PONGSONGGO	Dr. Ade Yolanda Latjuba, SS.,MA.
F051251017	2025	RIRIN	Dr. Mardi Adi Armin, M.Hum.
F051251028	2025	ARINI NUR FATWA	Dr. Mardi Adi Armin, M.Hum.
F051251040	2025	DHIA PALIMBU	Dr. Mardi Adi Armin, M.Hum.
F051201050	2020	MUH. ALI IMRAN	Dr. Mardi Adi Armin, M.Hum.
F051211024	2021	NUR SULFIANI MUHRANI	Dr. Mardi Adi Armin, M.Hum.
F051221004	2022	AQILAH RAMADHANI ANHAR	Dr. Mardi Adi Armin, M.Hum.
F051221013	2022	RIRI MEISA PRATIWI	Dr. Mardi Adi Armin, M.Hum.
F051221018	2022	DIAN ADILAH AZIZAH	Dr. Mardi Adi Armin, M.Hum.
F051221034	2022	KEZIA AURORA MAPPA	Dr. Mardi Adi Armin, M.Hum.
F051221035	2022	FARAH HERDIANA	Dr. Mardi Adi Armin, M.Hum.
F051211022	2021	RALLY PUTRI AUDYNIA MERCYANY APRILIA	Alung, S.S., M.A.
F051231055	2023	HASNIATI	Alung, S.S., M.A.
F051231059	2023	NOVLIRAYANA PIDUN	Alung, S.S., M.A.
F051231061	2023	BEDRYS OWIN BORO SIRENDEN	Alung, S.S., M.A.
F051241002	2024	SUHARTIN SRI WARDANI	Alung, S.S., M.A.
F051241003	2024	TENGKU DAFISYAH ZAFIRA RAMADAN	Alung, S.S., M.A.
F051241009	2024	KARINI DEWI	Alung, S.S., M.A.
F051241028	2024	ATU HERLIANI MISA	Alung, S.S., M.A.
F051241033	2024	MUHAMMAD REZA RABBANI	Alung, S.S., M.A.
F051241039	2024	ALIEF NUGRAHA RUSTAN	Alung, S.S., M.A.
F051241049	2024	MUHAMMAD OFICK	Alung, S.S., M.A.
F051241056	2024	M. AL-FAUZAN MATTULADA	Alung, S.S., M.A.
F051241059	2024	FIKRIYAH MUSTANIRAH	Alung, S.S., M.A.
F051241062	2024	ALVIA DWI AL FADILLAH	Alung, S.S., M.A.
F051241079	2024	MA'RUFAH	Alung, S.S., M.A.
"""

lines = raw_data.strip().split("\n")
for line in lines:
        parts = line.split("\t")
        if len(parts) >= 4:
            nim = parts[0].strip()
            # year = parts[1].strip()
            # student_name = parts[2].strip()
            pa_name = parts[3].strip()
            
            # Find/Upsert the Advisor
            adv = db.query(Advisor).filter(Advisor.nama.ilike(f"%{pa_name}%")).first()
            if not adv:
                # If advisor doesn't exist, we must create a User for them too
                username = f"PA_{nim}" # Fallback username if none, wait... let's just use part of their name
                username = "".join(filter(str.isalpha, pa_name))[:8].upper()
                # Let's generate a pseudo nip:
                username = "NIP_" + ("".join(filter(str.isalpha, pa_name))[:6].upper())
                
                u = db.query(User).filter(User.username == username).first()
                if not u:
                    u = User(username=username, hashed_password=hashed, role="ADVISOR")
                    db.add(u)
                    db.flush()
                
                adv = Advisor(user_id=u.id, nama=pa_name)
                db.add(adv)
                db.flush()
            
            # Connect the student
            st = db.query(Student).filter(Student.nim == nim).first()
            if st:
                st.advisor_id = adv.id
                linked += 1
            else:
                not_found_students.append(nim)

db.commit()
print(f"BOM MAPPING COMPLETE. Successfully linked {linked} specific real students.")
if not_found_students:
    print(f"Warning, {len(not_found_students)} students not found in DB: {not_found_students}")
else:
    print("All provided students successfully located and mapped!")
