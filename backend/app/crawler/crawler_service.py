import re
import urllib.parse
from typing import List, Dict, Any, Optional, Set
from bs4 import BeautifulSoup
import httpx
from app.config import settings

try:
    from langchain_community.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class UJAqabaCrawlerEngine:
    """
    Autonomous University Ingestion Engine dedicated specifically to
    the University of Jordan - Aqaba Branch Portal (https://aqaba.ju.edu.jo/).
    """
    
    ALLOWED_DOMAIN = "aqaba.ju.edu.jo"

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout
        if LANGCHAIN_AVAILABLE:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", " ", ""]
            )
        else:
            self.text_splitter = None

    def is_allowed_aqaba_url(self, url: str) -> bool:
        """Domain boundary constraint enforcing target: https://aqaba.ju.edu.jo/"""
        if not url:
            return False
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        return netloc == self.ALLOWED_DOMAIN or netloc.endswith(f".{self.ALLOWED_DOMAIN}")

    def get_seed_urls(self) -> List[str]:
        return settings.seed_urls

    async def fetch_page(self, url: str) -> Optional[str]:
        if not self.is_allowed_aqaba_url(url):
            print(f"[Crawler Engine] Skipping off-domain URL: {url}")
            return None

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) UJ-Aqaba-Crawler/2.0"})
                if resp.status_code == 200:
                    return resp.text
        except Exception as e:
            print(f"[Crawler Engine Warning] Failed to fetch {url}: {e}")
        return None

    def parse_html(self, html_content: str, url: str) -> Dict[str, Any]:
        soup = BeautifulSoup(html_content, "html.parser")

        # Strip ASP.NET hidden inputs
        for hidden_input in soup.find_all("input", {"type": "hidden"}):
            hidden_input.decompose()

        # Strip non-content UI elements
        for element in soup(["script", "style", "nav", "footer", "header", "form", "noscript"]):
            element.decompose()

        # Extract Page Title
        title = soup.title.string.strip() if soup.title and soup.title.string else "الجامعة الأردنية فرع العقبة"

        # Extract Tables
        tables = []
        for tbl in soup.find_all("table"):
            rows = []
            for tr in tbl.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells and any(cells):
                    rows.append(" | ".join(cells))
            if rows:
                tables.append("\n".join(rows))

        # Extract PDF Links
        pdf_links = []
        child_links: Set[str] = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith("javascript:") or href.startswith("#"):
                continue

            full_link = urllib.parse.urljoin(url, href).split("#")[0]
            if self.is_allowed_aqaba_url(full_link):
                if full_link.lower().endswith(".pdf") or ".pdf?" in full_link.lower():
                    pdf_links.append({"text": a_tag.get_text(strip=True) or "PDF Document", "link": full_link})
                elif full_link.lower().endswith((".aspx", ".html", ".htm", "/")) or "/arabic/" in full_link.lower():
                    child_links.add(full_link)

        # Extract Clean Core Text
        clean_text = soup.get_text(separator="\n", strip=True)
        clean_text = re.sub(r'\n+', '\n', clean_text)

        return {
            "url": url,
            "title": title,
            "clean_text": clean_text,
            "tables": tables,
            "pdf_links": pdf_links,
            "child_links": list(child_links),
            "raw_html": html_content
        }

    def chunk_text(self, text: str) -> List[str]:
        if self.text_splitter:
            return self.text_splitter.split_text(text)
        else:
            paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
            chunks = []
            current = ""
            for p in paragraphs:
                if len(current) + len(p) > 500:
                    chunks.append(current)
                    current = p
                else:
                    current = f"{current}\n{p}" if current else p
            if current:
                chunks.append(current)
            return chunks

crawler_engine = UJAqabaCrawlerEngine()

if __name__ == "__main__":
    import asyncio
    from app.crawler.scheduler import trigger_immediate_sync
    
    async def run_crawler_test():
        print("=== [Crawler & Ingestion Test - University of Jordan (Aqaba)] ===")
        print(f"Target Domain: {crawler_engine.ALLOWED_DOMAIN}")
        seeds = crawler_engine.get_seed_urls()
        print(f"Configured Seed URLs: {len(seeds)}")
        print("\n[Crawler Engine] Testing baseline sync & SHA-256 change detection...")
        results = await trigger_immediate_sync()
        synced = sum(1 for r in results if r.get("status") in ("updated", "unchanged"))
        failed = sum(1 for r in results if r.get("status") == "failed")
        print(f"\n[Summary] {synced} sources active/cached, {failed} unreachable.")
        print("=== [Ingestion Test Completed Successfully] ===")

    asyncio.run(run_crawler_test())
