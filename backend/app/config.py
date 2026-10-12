import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "دليل الطالب الأكاديمي الذكي - الجامعة الأردنية فرع العقبة"
    VERSION: str = "2.0.0"
    
    GEMINI_API_KEY: str = ""
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "uj_academic_assistant"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # Target University of Jordan & Aqaba Branch Portals
    UNIVERSITY_BASE_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Home.aspx"
    UJ_AQABA_DOMAIN: str = "https://aqaba.ju.edu.jo"
    ALLOWED_DOMAIN_PATTERN: str = r"^https?://.*\.ju\.edu\.jo.*"
    
    # Core Official University Endpoints & Sub-portals
    AQABA_HOME_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Home.aspx"
    REGISTRATION_UNITS_URL: str = "https://aqaba.ju.edu.jo/units/Registration/Home.aspx"
    GRADUATE_STUDIES_URL: str = "https://graduatedstudies.ju.edu.jo/Home.aspx"
    ACADEMICS_FACULTIES_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx"
    ADMINISTRATIVE_SERVICES_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Pages/Administrative.aspx"
    SELF_REGISTRATION_APP_URL: str = "https://ujapps.ju.edu.jo/selfregappaq/home.xhtml"
    SELF_REGISTRATION_AQABA_URL: str = "https://ujapps.ju.edu.jo/selfregappaq/home.xhtml"

    ELEARNING_PORTAL_URL: str = "https://elearning.ju.edu.jo/"
    YEARBOOK_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Lists/Yearbook/yearbook.aspx"
    
    # E-Services, News & Library Portals
    COMPLAINTS_SYSTEM_URL: str = "https://eservices.ju.edu.jo/complaintsys/login.aspx"
    NEWS_PORTAL_URL: str = "https://news.ju.edu.jo/Home.aspx"
    LIBRARY_PORTAL_URL: str = "https://library.ju.edu.jo/NEWLIBRARY/EN_Library/Default.aspx"
    
    # Faculty Sub-Pages
    AQABA_IT_FACULTY_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Faculties/IT/Home.aspx"
    AQABA_BUSINESS_FACULTY_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Faculties/Business/Home.aspx"
    AQABA_MARINE_FACULTY_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Faculties/Marine/Home.aspx"
    AQABA_TOURISM_FACULTY_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Faculties/Tourism/Home.aspx"
    AQABA_LANGUAGES_FACULTY_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Faculties/Languages/Home.aspx"
    AQABA_NURSING_FACULTY_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Faculties/Nursing/Home.aspx"
    
    # Deanships & Academic Bylaws
    AQABA_STUDENT_AFFAIRS_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Deanships/StudentAffairs/Home.aspx"
    AQABA_REGISTRATION_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Deanships/Registration/Home.aspx"
    AQABA_ADMISSION_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Deanships/Admission/Home.aspx"
    AQABA_CALENDAR_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Deanships/Registration/Calendar.aspx"
    AQABA_BYLAWS_URL: str = "https://aqaba.ju.edu.jo/ar/arabic/Deanships/Registration/Instructions.aspx"
    
    @property
    def seed_urls(self) -> List[str]:
        return [
            self.AQABA_HOME_URL,
            self.REGISTRATION_UNITS_URL,
            self.GRADUATE_STUDIES_URL,
            self.ACADEMICS_FACULTIES_URL,
            self.ADMINISTRATIVE_SERVICES_URL,
            self.SELF_REGISTRATION_APP_URL,
            self.ELEARNING_PORTAL_URL,
            self.YEARBOOK_URL,
            self.COMPLAINTS_SYSTEM_URL,
            self.NEWS_PORTAL_URL,
            self.LIBRARY_PORTAL_URL,
            self.AQABA_IT_FACULTY_URL,
            self.AQABA_BUSINESS_FACULTY_URL,
            self.AQABA_MARINE_FACULTY_URL,
            self.AQABA_TOURISM_FACULTY_URL,
            self.AQABA_LANGUAGES_FACULTY_URL,
            self.AQABA_NURSING_FACULTY_URL,
            self.AQABA_STUDENT_AFFAIRS_URL,
            self.AQABA_REGISTRATION_URL,
            self.AQABA_ADMISSION_URL,
            self.AQABA_CALENDAR_URL,
            self.AQABA_BYLAWS_URL
        ]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
