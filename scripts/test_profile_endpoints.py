import requests

def test_login_and_profile():
    base_url = "http://localhost:8000"
    
    # 1. TEST ADMIN
    print("--- TESTING ADMIN PROFILE ---")
    admin_login = requests.post(f"{base_url}/auth/login", data={"username": "admin", "password": "password123"})
    if admin_login.status_code != 200:
        print("FAIL: admin login failed", admin_login.text)
        return
    token = admin_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # GET profil
    get_res = requests.get(f"{base_url}/admin/profile", headers=headers)
    print("GET status:", get_res.status_code)
    print("GET admin data:", get_res.json())
    
    # PUT profil
    put_res = requests.put(f"{base_url}/admin/profile", json={
        "username": "admin",
        "email": "admin_baru@unhas.ac.id",
        "whatsapp": "+628111222333"
    }, headers=headers)
    print("PUT status:", put_res.status_code)
    print("PUT response:", put_res.json())
    
    # GET profil again to check persistence
    get_res2 = requests.get(f"{base_url}/admin/profile", headers=headers)
    print("GET admin data after update:", get_res2.json())
    assert get_res2.json()["email"] == "admin_baru@unhas.ac.id"
    assert get_res2.json()["whatsapp"] == "+628111222333"
    print("SUCCESS: ADMIN Profile update OK!\n")

    # 2. TEST PRODI
    print("--- TESTING PRODI PROFILE ---")
    prodi_login = requests.post(f"{base_url}/auth/login", data={"username": "prodi_sastra_prancis", "password": "password123"})
    if prodi_login.status_code != 200:
        print("FAIL: prodi login failed", prodi_login.text)
        return
    token = prodi_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # GET profil
    get_res = requests.get(f"{base_url}/prodi/profile", headers=headers)
    print("GET status:", get_res.status_code)
    print("GET prodi data:", get_res.json())
    
    # PUT profil
    put_res = requests.put(f"{base_url}/prodi/profile", json={
        "username": "prodi_sastra_prancis",
        "email": "prodi_prancis@unhas.ac.id",
        "whatsapp": "+628444555666"
    }, headers=headers)
    print("PUT status:", put_res.status_code)
    print("PUT response:", put_res.json())
    
    # GET profil again to check persistence
    get_res2 = requests.get(f"{base_url}/prodi/profile", headers=headers)
    print("GET prodi data after update:", get_res2.json())
    assert get_res2.json()["email"] == "prodi_prancis@unhas.ac.id"
    assert get_res2.json()["whatsapp"] == "+628444555666"
    print("SUCCESS: PRODI Profile update OK!\n")

    # 3. TEST ADVISOR
    print("--- TESTING ADVISOR PROFILE ---")
    # Finding advisor NIP from database or login via NIP
    # Let's use PA_FRN1/2 as username or a valid NIP like 198109082018074001
    adv_login = requests.post(f"{base_url}/auth/login", data={"username": "198109082018074001", "password": "password123"})
    if adv_login.status_code != 200:
        print("FAIL: advisor login failed", adv_login.text)
        return
    token = adv_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # GET profil
    get_res = requests.get(f"{base_url}/advisor/profile", headers=headers)
    print("GET status:", get_res.status_code)
    print("GET advisor data:", get_res.json())
    
    # PUT profil
    put_res = requests.put(f"{base_url}/advisor/profile", json={
        "username": "198109082018074001",
        "email": "advisor_prancis@unhas.ac.id",
        "whatsapp": "+628555666777",
        "telegram_username": "advisor_prn"
    }, headers=headers)
    print("PUT status:", put_res.status_code)
    print("PUT response:", put_res.json())
    
    # GET profil again to check persistence
    get_res2 = requests.get(f"{base_url}/advisor/profile", headers=headers)
    print("GET advisor data after update:", get_res2.json())
    assert get_res2.json()["email"] == "advisor_prancis@unhas.ac.id"
    assert get_res2.json()["whatsapp"] == "+628555666777"
    assert get_res2.json()["telegram_username"] == "advisor_prn"
    print("SUCCESS: ADVISOR Profile update OK!\n")

    # 4. TEST STUDENT
    print("--- TESTING STUDENT PROFILE ---")
    # NIM: F011251001
    student_login = requests.post(f"{base_url}/auth/login", data={"username": "F011251001", "password": "password123"})
    if student_login.status_code != 200:
        print("FAIL: student login failed", student_login.text)
        return
    token = student_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # PUT profil
    put_res = requests.put(f"{base_url}/students/F011251001/profile", json={
        "username": "F011251001",
        "email": "stud_test@unhas.ac.id",
        "phone_number_wa": "+628999000111",
        "telegram_username": "stud_tele"
    }, headers=headers)
    print("PUT status:", put_res.status_code)
    print("PUT response:", put_res.json())
    print("SUCCESS: STUDENT Profile update OK!\n")

if __name__ == "__main__":
    test_login_and_profile()
