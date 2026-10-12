import asyncio
from app.config import settings
from app.crawler.scraper import scraper
from app.crawler.change_detector import change_detector

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    APSCHEDULER_AVAILABLE = True
    scheduler = AsyncIOScheduler()
except ImportError:
    APSCHEDULER_AVAILABLE = False
    scheduler = None

async def scheduled_crawler_job():
    """Periodic background job checking SHA-256 diffs for UJ sub-portals."""
    print("[APScheduler] Executing periodic UJ portal web ingestion & change detection scan...")
    try:
        results = []
        # First sync baseline seed dataset
        for seed in scraper.get_seed_dataset():
            res = await change_detector.sync_page_data(seed["url"], scraped_data=seed)
            results.append(res)

        # Sync target seed URLs
        for url in settings.seed_urls:
            res = await change_detector.sync_page_data(url)
            results.append(res)

        updated_count = sum(1 for r in results if r.get("status") == "updated")
        print(f"[APScheduler] Portal sync completed. {updated_count} pages updated in vector store.")
    except Exception as e:
        print(f"[APScheduler Error] Background crawler job failed: {e}")

def start_crawler_scheduler(interval_hours: int = 12):
    """Start APScheduler for periodic change detection scanning."""
    if APSCHEDULER_AVAILABLE and scheduler and not scheduler.running:
        scheduler.add_job(
            scheduled_crawler_job,
            trigger="interval",
            hours=interval_hours,
            id="uj_periodic_crawler",
            replace_existing=True
        )
        scheduler.start()
        print(f"[APScheduler] Background UJ portal scanner started (Interval: {interval_hours} Hours).")
    else:
        print("[APScheduler Warning] APScheduler is not installed. Background periodic scanning disabled.")

async def trigger_immediate_sync() -> list:
    """Trigger immediate crawler sync scan for all seed URLs."""
    results = []
    for seed in scraper.get_seed_dataset():
        res = await change_detector.sync_page_data(seed["url"], scraped_data=seed)
        results.append(res)

    for url in settings.seed_urls:
        res = await change_detector.sync_page_data(url)
        results.append(res)

    return results
