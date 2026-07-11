import os
from pydantic_settings import BaseSettings

class ScraperConfig(BaseSettings):
    """
    Konfigurasi rahasia untuk modul Scraper AIMS.
    AWAS: Karena alasan etika & regulasi privasi data, Anda (sebagai administrator sistem)
    diwajibkan mengisi URL spesifik Universitas Anda ('neosia.unhas.ac.id' atau serupa)
    dan kredensial login secara mandiri pada environment variables (.env) atau mengisi langsung di sini.
    """
    
    # 1. URL Login Sistem Akademik Universitas (Contoh: "https://backoffice.neosia.unhas.ac.id/login")
    TARGET_PORTAL_LOGIN_URL: str = os.getenv("SCRAPER_LOGIN_URL", "https://portal.example-university.com/login")
    TARGET_PORTAL_GRADES_URL: str = os.getenv("SCRAPER_GRADES_URL", "https://portal.example-university.com/grades")
    
    # 2. Kredensial Login (Harus berupa akun super-admin atau read-only yang diberikan kampus)
    SCRAPER_USERNAME: str = os.getenv("SCRAPER_USERNAME", "admin_aims_default")
    SCRAPER_PASSWORD: str = os.getenv("SCRAPER_PASSWORD", "secret_pass_123")
    
    # 3. HTML/CSS Selectors (Harus disesuaikan dengan desain kode HTML website Universitas Anda)
    SELECTOR_INPUT_USERNAME: str = os.getenv("SELECTOR_USERNAME", "#username")
    SELECTOR_INPUT_PASSWORD: str = os.getenv("SELECTOR_PASSWORD", "#password")
    SELECTOR_BTN_LOGIN: str = os.getenv("SELECTOR_BTN_LOGIN", "button[type='submit']")
    
    # Selector untuk menavigasi tabel nilai
    SELECTOR_TABLE_ROW: str = os.getenv("SELECTOR_TABLE_ROW", "table.grades tbody tr")
    SELECTOR_CELL_NIM: str = os.getenv("SELECTOR_CELL_NIM", "td.nim")
    SELECTOR_CELL_IPK: str = os.getenv("SELECTOR_CELL_IPK", "td.ipk")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

config = ScraperConfig()
