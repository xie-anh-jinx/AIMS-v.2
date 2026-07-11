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
            run_daily_evaluation()
        else:
            logger.warning("[Scheduler] No data scraped or scraping failed. Check config and network.")
    except Exception as e:
        logger.error(f"[Scheduler] Scraper failed: {e}")

def run_daily_evaluation():
    """Triggered by scheduler to evaluate all students automatically"""
    logger.info("[Scheduler] Executing scheduled academic evaluation...")
    engine = WorkflowEngine()
    result = engine.run_full_evaluation()
    logger.info(f"[Scheduler] Evaluation complete: {result}")

def start_scheduler():
    """Initializes and starts the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Skrip Scraping berjalan sebulan sekali pada tengah malam awal bulan misal
    scheduler.add_job(
        run_monthly_extraction,
        trigger=CronTrigger(day="1", hour="2", minute="0"),
        id="monthly_headless_extraction",
        name="Scrape Legacy Siakad Grades",
        replace_existing=True,
    )
    
    # In production, this might run every day at 01:00 AM.
    # For AIMS demo, we run it every hour to see it working, 
    # or you can test it directly via API.
    scheduler.add_job(
        run_daily_evaluation,
        trigger=CronTrigger(hour="*", minute="0"),
        id="daily_academic_eval",
        name="Evaluate student academic risks",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info("[Scheduler] Background scheduler started successfully.")
    return scheduler
