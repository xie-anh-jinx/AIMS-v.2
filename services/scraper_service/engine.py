import asyncio
import logging
from typing import List, Dict
from playwright.async_api import async_playwright, TimeoutError
from .config import config

logger = logging.getLogger(__name__)

class ScraperEngine:
    def __init__(self):
        self.login_url = config.TARGET_PORTAL_LOGIN_URL
        self.grades_url = config.TARGET_PORTAL_GRADES_URL
        
    async def extract_all_grades(self) -> List[Dict[str, str]]:
        """
        Fungsi abstrak untuk mengekstrak data dari portal akademik.
        Ini menggunakan Headless Browser (Chromium) untuk mensimulasikan login manusia.
        """
        extracted_data = []
        
        logger.info(f"[SCRAPER] Memulai ekstraksi data dari {self.login_url}")
        
        async with async_playwright() as p:
            # Gunakan headless=True di server production
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # 1. Navigasi ke Halaman Login
                await page.goto(self.login_url, wait_until="networkidle")
                
                # 2. Proses Login
                logger.info("[SCRAPER] Melakukan injeksi kredensial...")
                await page.fill(config.SELECTOR_INPUT_USERNAME, config.SCRAPER_USERNAME)
                await page.fill(config.SELECTOR_INPUT_PASSWORD, config.SCRAPER_PASSWORD)
                
                # Klik tombol login dan tunggu navigasi selesai
                async with page.expect_navigation(timeout=10000):
                    await page.click(config.SELECTOR_BTN_LOGIN)
                    
                logger.info("[SCRAPER] Login Berhasil. Menuju ke halaman Transkrip Nilai...")
                
                # 3. Navigasi ke Halaman Nilai
                await page.goto(self.grades_url, wait_until="networkidle")
                
                # 4. Melakukan Parsing Tabel menggunakan selector dari config.py
                # Tunggu hingga tabel muncul
                await page.wait_for_selector(config.SELECTOR_TABLE_ROW, timeout=5000)
                
                rows = await page.query_selector_all(config.SELECTOR_TABLE_ROW)
                logger.info(f"[SCRAPER] Menemukan {len(rows)} baris data mahasiswa. Mulai proses penyalinan.")
                
                for row in rows:
                    nim_el = await row.query_selector(config.SELECTOR_CELL_NIM)
                    ipk_el = await row.query_selector(config.SELECTOR_CELL_IPK)
                    
                    if nim_el and ipk_el:
                        nim_text = await nim_el.inner_text()
                        ipk_text = await ipk_el.inner_text()
                        
                        extracted_data.append({
                            "nim": nim_text.strip(),
                            "ipk": ipk_text.strip()
                        })
                        
                logger.info("[SCRAPER] Ekstraksi selesai dan berhasil disalin ke memori.")
                
            except TimeoutError:
                logger.error("[SCRAPER] Timeout! Elemen HTML tidak ditemukan di Web Universitas. Pastikan Selector di config.py sudah benar.")
            except Exception as e:
                logger.error(f"[SCRAPER] Terjadi kegagalan kritis saat scraping: {str(e)}")
            finally:
                await browser.close()
                
        return extracted_data

def run_scraper_job():
    """Fungsi pembungkus sinkron yang bisa dipanggil oleh APScheduler"""
    engine = ScraperEngine()
    
    # Karena APScheduler butuh fungsi sinkron, kita buat event loop sementara
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            task = loop.create_task(engine.extract_all_grades())
            # Jika dalam fastapi event loop, biarkan task jalan asinkron
            return task
        else:
            return loop.run_until_complete(engine.extract_all_grades())
    except RuntimeError:
        # Menangani case tidak ada event loop (Thread baru dari Cron)
        return asyncio.run(engine.extract_all_grades())

# Untuk uji coba lokal (python -m services.scraper_service.engine)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data = run_scraper_job()
    print("HASIL DATA:", data)
