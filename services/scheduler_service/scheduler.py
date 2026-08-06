import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.ai_agent_service.workflow_engine import WorkflowEngine
from services.scraper_service.engine import run_scraper_job

logger = logging.getLogger("SchedulerService")

def run_monthly_extraction():
    """Triggered by scheduler to scrape grades from the Legacy SIAKAD portal"""
    logger.info("[Scheduler] Executing Headless Browser Scraping Job...")
    try:
        scraped_data = run_scraper_job()
        if scraped_data:
            logger.info(f"[Scheduler] Successfully scraped {len(scraped_data)} records! Inserting to DB...")
            # Todo: Custom DB insertion logic here...
            
            # Setelah data ditarik, bangunkan AI Evaluator untuk mengkaji nilai baru tersebut
            run_monthly_evaluation()
        else:
            logger.warning("[Scheduler] No data scraped or scraping failed. Check config and network.")
    except Exception as e:
        logger.error(f"[Scheduler] Scraper failed: {e}")

def run_monthly_evaluation():
    """Triggered by scheduler to evaluate all students and dispatch PA notifications once per month"""
    logger.info("[Scheduler] Executing scheduled monthly academic evaluation...")
    engine = WorkflowEngine()
    result = engine.run_full_evaluation()
    logger.info(f"[Scheduler] Monthly evaluation complete: {result}")

def start_scheduler():
    """Initializes and starts the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Skrip Scraping berjalan sebulan sekali pada tengah malam awal bulan (Tanggal 1, 02:00 AM)
    scheduler.add_job(
        run_monthly_extraction,
        trigger=CronTrigger(day="1", hour="2", minute="0"),
        id="monthly_headless_extraction",
        name="Scrape Legacy Siakad Grades",
        replace_existing=True,
    )
    
    # Evaluasi Akademik & Pengiriman Catatan PA Otomatis dieksekusi 1X SEBULAN 
    # (Tanggal 1 pukul 08:00 AM) agar tidak mengganggu Penasihat Akademik secara berlebihan.
    scheduler.add_job(
        run_monthly_evaluation,
        trigger=CronTrigger(day="1", hour="8", minute="0"),
        id="monthly_academic_eval",
        name="Evaluate student academic risks monthly",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info("[Scheduler] Background scheduler started successfully (Monthly evaluation active).")
    return scheduler
