import re
import datetime
import urllib.parse
from typing import Dict, Any, List, Optional, Set
from bs4 import BeautifulSoup
import httpx
from app.config import settings

class UJWebScraper:
    """
    University of Jordan & Aqaba Branch ASP.NET Web Scraper & HTML Cleaning Engine.
    Permits official University of Jordan domains (*.ju.edu.jo).
    """

    ALLOWED_DOMAINS = [
        "aqaba.ju.edu.jo",
        "graduatedstudies.ju.edu.jo",
        "ujapps.ju.edu.jo",
        "elearning.ju.edu.jo",
        "eservices.ju.edu.jo",
        "news.ju.edu.jo",
        "library.ju.edu.jo",
        "www.ju.edu.jo",
        "ju.edu.jo"
    ]

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) UJ-Academic-Assistant/2.0"
        }

    def is_allowed_aqaba_url(self, url: str) -> bool:
        """Domain boundary constraint enforcing target University of Jordan domains (*.ju.edu.jo)."""
        if not url:
            return False
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        return any(netloc == domain or netloc.endswith(f".{domain}") for domain in self.ALLOWED_DOMAINS)

    def detect_category(self, url: str, text: str) -> str:
        u_lower = url.lower()
        t_lower = text.lower()
        if "complaintsys" in u_lower or "eservices" in u_lower or "شكاوى" in t_lower or "اقتراحات" in t_lower:
            return "complaints_and_suggestions"
        elif "news" in u_lower or "أخبار" in t_lower or "أحداث" in t_lower or "مؤتمر" in t_lower:
            return "news_and_events"
        elif "library" in u_lower or "مكتبة" in t_lower or "كتب" in t_lower or "دورية" in t_lower:
            return "library_services"
        elif "graduatedstudies" in u_lower or "دراسات عليا" in t_lower or "ماجستير" in t_lower or "دكتوراة" in t_lower:
            return "graduate_studies"
        elif "regapp" in u_lower or "تسجيل ذاتي" in t_lower or "تسجيل مواد" in t_lower:
            return "self_registration"
        elif "elearning" in u_lower or "تعليم إلكتروني" in t_lower or "مودل" in t_lower:
            return "elearning"
        elif "yearbook" in u_lower or "كتاب سنوي" in t_lower or "خريجين" in t_lower:
            return "yearbook"
        elif "administrative" in u_lower or "إدارية" in t_lower or "مالية" in t_lower or "خدمات" in t_lower:
            return "administrative_services"
        elif "academics" in u_lower or "كليات" in t_lower or "تخصصات" in t_lower:
            return "academics"
        elif "reg" in u_lower or "calendar" in t_lower or "تقويم" in t_lower or "سحب" in t_lower:
            return "calendar"
        elif "bylaw" in u_lower or "instruction" in u_lower or "تعليمات" in t_lower or "قوانين" in t_lower:
            return "bylaw"
        elif "facult" in u_lower or "كلية" in t_lower or "عميد" in t_lower or "قسم" in t_lower:
            return "faculty_info"
        elif "admiss" in u_lower or "قبول" in t_lower:
            return "admissions"
        elif "scholar" in u_lower or "منح" in t_lower:
            return "scholarship"
        return "general_portal"

    async def scrape_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch and parse ASP.NET HTML page from official UJ domain."""
        if not self.is_allowed_aqaba_url(url):
            print(f"[Scraper Rejected] URL {url} is outside UJ domain boundary.")
            return None

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code == 200:
                    last_mod = resp.headers.get("Last-Modified") or datetime.datetime.utcnow().isoformat()
                    return self.clean_and_extract(resp.text, str(resp.url), last_modified=last_mod)
        except Exception as e:
            print(f"[Scraper Warning] Failed to fetch {url}: {e}")
        return None

    def is_chrome_line(self, line: str) -> bool:
        line_clean = line.strip().lower()
        if not line_clean:
            return True
        
        chrome_keywords = [
            "student registration", "نظام تسجيل الطلبة", "استعادة كلمة السر",
            "reset password", "microsoft account", "حساب مايكروسوفت", "دخول",
            "log in", "sign in", "forget password", "نسيت كلمة السر",
            "جميع الحقوق محفوظة", "شروط الاستخدام", "سياسة الخصوصية", "cookie",
            "skip to content", "english", "عربي", "main menu", "login.aspx"
        ]
        
        for kw in chrome_keywords:
            if line_clean == kw or (len(line_clean) < 60 and kw in line_clean):
                return True
                
        return False

    def clean_and_extract(self, html_content: str, url: str, last_modified: str = None) -> Dict[str, Any]:
        soup = BeautifulSoup(html_content, "html.parser")

        # Strip ASP.NET hidden form elements and state fields
        for hidden_input in soup.find_all("input", {"type": "hidden"}):
            hidden_input.decompose()

        # Strip forms (login/registration UI)
        for form in soup.find_all("form"):
            # If form looks like login or ASP.NET authentication, decompose
            form_text = form.get_text().lower()
            if any(k in form_text for k in ["login", "password", "دخول", "كلمة السر"]):
                form.decompose()

        # Strip non-essential UI/decorative elements, navigation, and scripts
        for elem in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe", "aside", "form"]):
            elem.decompose()

        # Strip class selectors for ads or social sharing / navigation menus
        for elem in soup.find_all(class_=re.compile(r'(ad|banner|share|social|footer|sidebar|top-bar|main-menu|login|nav|menu)', re.I)):
            elem.decompose()

        # Extract Page Title & Headings Hierarchy
        title = "الجامعة الأردنية - البوابة الأكاديمية الرسمية"
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"]) if h.get_text(strip=True)]

        # Extract Tabular Data
        tables = []
        for tbl in soup.find_all("table"):
            rows = []
            for tr in tbl.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells and any(cells):
                    rows.append(" | ".join(cells))
            if rows:
                tables.append("\n".join(rows))

        # Extract Child Links matching UJ domains
        child_links: Set[str] = set()
        pdf_links: List[Dict[str, str]] = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith("javascript:") or href.startswith("#"):
                continue

            full_link = urllib.parse.urljoin(url, href).split("#")[0]
            if self.is_allowed_aqaba_url(full_link):
                if full_link.lower().endswith(".pdf") or ".pdf?" in full_link.lower():
                    pdf_links.append({"text": a_tag.get_text(strip=True) or "مستند PDF", "link": full_link})
                else:
                    child_links.add(full_link)

        # Extract Clean Core Text, filtering chrome lines
        raw_lines = soup.get_text(separator="\n", strip=True).split("\n")
        clean_lines = [l.strip() for l in raw_lines if l.strip() and not self.is_chrome_line(l)]
        clean_text = "\n".join(clean_lines)
        clean_text = re.sub(r'\n+', '\n', clean_text)

        category = self.detect_category(url, clean_text)
        if not last_modified:
            last_modified = datetime.datetime.utcnow().isoformat()

        return {
            "title": title,
            "source_url": url,
            "url": url,
            "last_modified": last_modified,
            "category": category,
            "section_category": category,
            "headings": headings,
            "clean_text": clean_text,
            "tables": tables,
            "pdf_links": pdf_links,
            "child_links": list(child_links),
            "raw_html": html_content
        }

    def get_seed_dataset(self) -> List[Dict[str, Any]]:
        """Static seed data covering all official UJ & UJ Aqaba URLs provided by user."""
        now_str = datetime.datetime.utcnow().isoformat()
        return [
            {
                "title": "نظام الشكاوى والاقتراحات الإلكتروني - الجامعة الأردنية",
                "source_url": settings.COMPLAINTS_SYSTEM_URL,
                "url": settings.COMPLAINTS_SYSTEM_URL,
                "last_modified": now_str,
                "category": "complaints_and_suggestions",
                "section_category": "complaints_and_suggestions",
                "headings": ["نظام الشكاوى والاقتراحات الإلكتروني", "بوابة صوت الطالب والخدمات الإلكترونية"],
                "clean_text": """
                نظام الشكاوى والاقتراحات الإلكتروني بالجامعة الأردنية (https://eservices.ju.edu.jo/complaintsys/login.aspx):
                يسمح للطلبة وأعضاء الهيئة التدريسية والإدارية بتقديم الشكاوى، المقترحات، والملاحظات الأكاديمية والإدارية ومتابعة حالة الطلب إلكترونياً وبسرية تامة.
                خطوات تقديم الشكوى: تسجيل الدخول بالرقم الجامعي أو الوظيفي، اختيار نوع الطلب (أكاديمي/إداري/خدماتي)، كتابة نص الشكوى أو الملاحظة، وإرفاق المستندات إن وجدت.
                """,
                "tables": ["نظام الشكاوى | https://eservices.ju.edu.jo/complaintsys/login.aspx | الدخول بالرقم الجامعي"],
                "pdf_links": [],
                "child_links": []
            },
            {
                "title": "موقع أخبار الجامعة الأردنية والفعاليات الرسمية",
                "source_url": settings.NEWS_PORTAL_URL,
                "url": settings.NEWS_PORTAL_URL,
                "last_modified": now_str,
                "category": "news_and_events",
                "section_category": "news_and_events",
                "headings": ["أخبار الجامعة الأردنية", "الفعاليات والمؤتمرات والقرارات الأكاديمية"],
                "clean_text": """
                موقع أخبار الجامعة الأردنية (https://news.ju.edu.jo/Home.aspx): المركز الإعلامي الرسمي لنشر قرارات مجلس العمداء، إعلانات القبول والتسجيل، المؤتمرات العلمية، الفعاليات الثقافية والرياضية، وأخبار فرع العقبة.
                """,
                "tables": ["المركز الإعلامي | news.ju.edu.jo | البريد: news@ju.edu.jo"],
                "pdf_links": [],
                "child_links": []
            },
            {
                "title": "المكتبة المركزية وقواعد البيانات الإلكترونية - الجامعة الأردنية",
                "source_url": settings.LIBRARY_PORTAL_URL,
                "url": settings.LIBRARY_PORTAL_URL,
                "last_modified": now_str,
                "category": "library_services",
                "section_category": "library_services",
                "headings": ["المكتبة المركزية والمصادر الإلكترونية", "الفهرس الآلي والمجلا ت والمطالعة الرقمية"],
                "clean_text": """
                مكتبة الجامعة الأردنية المركزية (https://library.ju.edu.jo/NEWLIBRARY/EN_Library/Default.aspx):
                تتيح للطلبة والباحثين بفرع العقبة والمركز الرئيسي الوصول إلى الفهرس الآلي، الكتب الرقمية، الرسائل الجامعية (أطروحات الماجستير والدكتوراة)، وقواعد البيانات العالمية مثل IEEE Xplore, ScienceDirect, Springer, JSTOR.
                ساعات دوام المكتبة: من الأحد إلى الخميس 08:00 صباحاً حتى 04:00 مساءً.
                """,
                "tables": ["المكتبة المركزية | library.ju.edu.jo | البريد: library@ju.edu.jo"],
                "pdf_links": [{"text": "دليل استخدام قواعد البيانات العالمية.pdf", "link": "https://library.ju.edu.jo/docs/database_guide.pdf"}],
                "child_links": []
            },
            {
                "title": "نظام تسجيل الطلبة - فرع العقبة (بوابة التسجيل الذاتي RegApp Aqaba)",
                "source_url": settings.SELF_REGISTRATION_AQABA_URL,
                "url": settings.SELF_REGISTRATION_AQABA_URL,
                "last_modified": now_str,
                "category": "registration_services",
                "section_category": "registration_services",
                "headings": ["نظام تسجيل الطلبة - فرع العقبة", "بوابة التسجيل الذاتي إلكترونياً (RegApp Aqaba)"],
                "clean_text": """
                نظام تسجيل الطلبة - فرع العقبة (https://ujapps.ju.edu.jo/selfregappaq/home.xhtml):
                البوابة الإلكترونية الرسمية للتسجيل الذاتي لطلبة الجامعة الأردنية فرع العقبة.
                تتيح البوابة للطلبة: تسجيل المواد الدراسية، متابعة جدول المواد الساحبة والمضافة، استعراض كشف العلامات، متابعة الخطة الدراسية والحالة الأكاديمية، والاطلاع على الرسوم الدراسية.
                وحدة القبول والتسجيل بفرع العقبة مختصة بإجراءات القبول، تسديد الرسوم، وتنزيل الجدول الدراسي لطلبة البكالوريوس والدراسات العليا.
                خدمات الوحدة: إصدار كشوف العلامات، إثبات الطالب، معادلة المواد، ومتابعة السحب والإضافة.
                الموقع: مبنى القبول والتسجيل الرئيسي - فرع العقبة.
                """,
                "tables": ["نظام تسجيل الطلبة (العقبة) | ujapps.ju.edu.jo/selfregappaq/home.xhtml | reg.aqaba@ju.edu.jo"],
                "pdf_links": [],
                "child_links": []
            },
            {
                "title": "وحدة القبول والتسجيل - فرع العقبة (البكالوريوس)",
                "source_url": settings.REGISTRATION_UNITS_URL,
                "url": settings.REGISTRATION_UNITS_URL,
                "last_modified": now_str,
                "category": "calendar",
                "section_category": "calendar",
                "headings": ["وحدة القبول والتسجيل - فرع العقبة", "تسجيل المواد والتقويم الأكاديمي للبكالوريوس"],
                "clean_text": """
                وحدة القبول والتسجيل بفرع العقبة مختصة بإجراءات القبول، تسديد الرسوم، وتنزيل الجدول الدراسي لطلبة البكالوريوس.
                خدمات الوحدة: إصدار كشوف العلامات، إثبات الطالب، معادلة المواد، ومتابعة السحب والإضافة.
                الموقع: مبنى القبول والتسجيل الرئيسي - العقبة.
                """,
                "tables": ["خدمة القبول والتسجيل | reg.aqaba@ju.edu.jo | 032090400 ext 2100"],
                "pdf_links": [],
                "child_links": []
            },
            {
                "title": "كلية الدراسات العليا - الجامعة الأردنية",
                "source_url": settings.GRADUATE_STUDIES_URL,
                "url": settings.GRADUATE_STUDIES_URL,
                "last_modified": now_str,
                "category": "graduate_studies",
                "section_category": "graduate_studies",
                "headings": ["كلية الدراسات العليا", "برامج الماجستير والدكتوراة والدبلوم العالي"],
                "clean_text": """
                كلية الدراسات العليا - الجامعة الأردنية (https://graduatedstudies.ju.edu.jo/Home.aspx):
                تتولى كلية الدراسات العليا الإشراف والمتابعة الأكاديمية لجميع برامج الماجستير والدكتوراة والدبلوم العالي بالجامعة الأردنية وفرع العقبة.
                تشمل الخدمات: شروط القبول للدراسات العليا، خطط برامج الماجستير والدكتوراة، تعليمات مناقشة الرسائل والأطروحات الأكاديمية، والتقويم الأكاديمي للدراسات العليا.
                """,
                "tables": ["كلية الدراسات العليا | graduatedstudies.ju.edu.jo/Home.aspx | امتحان اللغة الوطني: النجاح 65% للتخصصات العلمية | 50% للإنسانية"],
                "pdf_links": [],
                "child_links": []
            }
        ]

scraper = UJWebScraper()
