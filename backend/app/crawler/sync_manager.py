from typing import Dict, Any, List
from app.crawler.scraper import scraper, UJWebScraper
from app.crawler.change_detector import change_detector, SHA256ChangeDetector

class ContentSyncManager:
    """Unified Content Sync Manager bridging Web Scraper & Change Detector."""

    def __init__(self):
        self.scraper = scraper
        self.change_detector = change_detector

    async def sync_url(self, url: str) -> Dict[str, Any]:
        return await self.change_detector.sync_page_data(url)

    async def run_full_sync(self) -> List[Dict[str, Any]]:
        results = []
        for seed in self.scraper.get_seed_dataset():
            res = await self.change_detector.sync_page_data(seed["url"], scraped_data=seed)
            results.append(res)
        return results

sync_manager = ContentSyncManager()
