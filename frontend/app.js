document.addEventListener("DOMContentLoaded", () => {
  const htmlDoc = document.documentElement;
  const themeBtn = document.getElementById("theme-btn");
  const themeIconSun = document.getElementById("theme-icon-sun");
  const themeIconMoon = document.getElementById("theme-icon-moon");

  const langBtn = document.getElementById("lang-btn");
  const langLabel = document.getElementById("lang-label");

  const navTitle = document.getElementById("nav-title");
  const navSubtitle = document.getElementById("nav-subtitle");

  const heroTitle1 = document.getElementById("hero-title-1");
  const heroTitle2 = document.getElementById("hero-title-2");
  const heroDesc = document.getElementById("hero-desc");
  const heroCta = document.getElementById("hero-cta");
  const heroCalendarCta = document.getElementById("hero-calendar-cta");

  const topicsTitle = document.getElementById("topics-title");
  const consoleTitle = document.getElementById("console-title");

  const emptyState = document.getElementById("empty-state");
  const emptyTitle = document.getElementById("empty-title");
  const emptyDesc = document.getElementById("empty-desc");

  const stat1n = document.getElementById("stat1-n");
  const stat1l = document.getElementById("stat1-l");
  const stat2n = document.getElementById("stat2-n");
  const stat2l = document.getElementById("stat2-l");
  const stat3n = document.getElementById("stat3-n");
  const stat3l = document.getElementById("stat3-l");

  const footerTitle = document.getElementById("footer-title");
  const footerCopy = document.getElementById("footer-copy");
  const footerCreator = document.getElementById("footer-creator");

  const chatStream = document.getElementById("chat-stream");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const topicCards = document.querySelectorAll(".topic-card");

  // Side Drawer & Live Clock Elements
  const sidebarToggleBtn = document.getElementById("sidebar-toggle-btn");
  const sidebarToggleLabel = document.getElementById("sidebar-toggle-label");
  const drawerCloseBtn = document.getElementById("drawer-close-btn");
  const drawerBackdrop = document.getElementById("drawer-backdrop");
  const sideDrawer = document.getElementById("side-drawer");
  const drawerTitle = document.getElementById("drawer-title");
  const drawerTabCalBtn = document.getElementById("drawer-tab-cal-btn");
  const drawerTabLinksBtn = document.getElementById("drawer-tab-links-btn");
  const drawerTabDeansBtn = document.getElementById("drawer-tab-deans-btn");
  const drawerCalView = document.getElementById("drawer-calendar-view");
  const drawerLinksView = document.getElementById("drawer-links-view");
  const drawerDeansView = document.getElementById("drawer-deans-view");
  const liveClockElem = document.getElementById("live-digital-clock");
  const liveDateElem = document.getElementById("live-calendar-date");
  const clockStatusTag = document.getElementById("clock-status-tag");
  const campusStatusPill = document.getElementById("campus-status-pill");

  // Calendar Header & Toolbar Elements
  const calBadgeTag = document.getElementById("cal-badge-tag");
  const calMainTitle = document.getElementById("cal-main-title");
  const calDesc = document.getElementById("cal-desc");
  const milestonesGrid = document.getElementById("milestones-grid");
  const calSearchInput = document.getElementById("cal-search-input");
  const calendarTableBody = document.getElementById("calendar-table-body");
  const drawerLinksGrid = document.getElementById("drawer-links-grid");
  const drawerDeansList = document.getElementById("drawer-deans-list");

  // Filter tabs
  const ftabAll = document.getElementById("ftab-all");
  const ftabReg = document.getElementById("ftab-reg");
  const ftabExam = document.getElementById("ftab-exam");
  const ftabHoliday = document.getElementById("ftab-holiday");
  const ftabAcademic = document.getElementById("ftab-academic");

  // Table Headers
  const calThDate = document.getElementById("cal-th-date");
  const calThDay = document.getElementById("cal-th-day");
  const calThEvent = document.getElementById("cal-th-event");
  const calThCat = document.getElementById("cal-th-cat");
  const calThAsk = document.getElementById("cal-th-ask");

  let currentTheme = localStorage.getItem("uj_theme") || "light";
  let currentLang = localStorage.getItem("uj_lang") || "ar";
  let sessionId = `session_${Date.now()}`;
  let isLoading = false;
  let currentCategory = "all";
  let currentSearchQuery = "";

  // Auto-detect API backend (Localhost during development, Hugging Face Space in production)
  const API_BASE_URL = (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    ? "http://localhost:8000"
    : "https://prince369darkness-my-rafeeq.hf.space";

  const i18n = {
    ar: {
      navTitle: "الجامعة الأردنية — فرع العقبة",
      navSubtitle: "دليل الطالب الأكاديمي المباشر",
      heroTitle1: "إجابة موثّقة،",
      heroTitle2: "من مصدر الجامعة الرسمي",
      heroDesc: "اسأل عن الكليات، أعضاء الهيئة التدريسية، التقويم الأكاديمي، والمواعيد — والدليل يستخرج الجواب مباشرة من صفحات بوابة الجامعة الأردنية فرع العقبة.",
      heroCta: "ابدأ السؤال",
      heroCalBtn: "📅 التقويم الجامعي 2026/2027",
      topicsTitle: "أكثر الأسئلة شيوعاً",
      consoleTitle: "المرشد الأكاديمي — متصل الآن",
      emptyTitle: "أهلاً بك في دليل الجامعة الأردنية الأكاديمي",
      emptyDesc: "اختر أحد الأسئلة الشائعة أعلاه، أو اكتب سؤالك للحصول على إجابة موثقة من صفحات بوابة الجامعة الأردنية فرع العقبة.",
      inputPlaceholder: "اكتب سؤالك الأكاديمي...",
      langBtnLabel: "English",
      studentLabel: "الطالب",
      botLabel: "رفيق — المرشد الأكاديمي",
      citationText: "المصدر الرسمي",
      errorMsg: "عذراً، حدث خطأ في الاتصال بالخادم الرئيسي. يرجى المحاولة لاحقاً.",
      unavailableMsg: "عذراً، هذه المعلومة غير متوفرة حالياً على صفحات البوابة الرسمية.",
      stat1n: "٦",
      stat1l: "كليات مغطّاة",
      stat2n: "عربي / إنجليزي",
      stat2l: "دعم كامل بلغتين",
      stat3n: "مباشر",
      stat3l: "من البوابة الرسمية",
      footerTitle: "الجامعة الأردنية — فرع العقبة",
      footerCopy: "© 2026 جميع الحقوق محفوظة — فرع IEEE الطلابي",
      footerCreator: "إعداد وتصميم: <strong>شهد الربايعة</strong>",
      sidebarToggleLabel: "التقويم والقائمة",
      drawerTitle: "دليل العقبة والتقويم",
      clockStatusTag: "توقيت العقبة المباشر",
      drawerTabCal: "📅 التقويم الجامعي 2026/2027",
      drawerTabLinks: "🔗 بوابات فرع العقبة",
      drawerTabDeans: "🎓 عمداء الكليات",
      campusOpen: "المكاتب: مفتوحة الآن (8ص - 3م)",
      campusClosed: "المكاتب: مغلقة الآن (دوام 8ص - 3م)",
      calBadgeTag: "التقويم الجامعي المعتمد 2026 / 2027",
      calMainTitle: "مواعيد وتقويم الجامعة الأردنية — فرع العقبة",
      calDesc: "المواعيد الرسمية المعتمدة الصادرة عن الجامعة ومجلس اتحاد الطلبة للفصل الأول: السحب والإضافة، الامتحانات، والإجازات.",
      ftabAll: "الكل (28)",
      ftabReg: "التسجيل والسحب",
      ftabExam: "الامتحانات والعلامات",
      ftabHoliday: "العطل والإجازات",
      ftabAcademic: "المسيرة الأكاديمية",
      calSearchPlaceholder: "ابحث عن موعد (امتحانات، سحب وإضافة، عطلة...)...",
      calThDate: "التاريخ",
      calThDay: "اليوم",
      calThEvent: "الموعد / الحدث الأكاديمي",
      calThCat: "التصنيف",
      calThAsk: "استفسار",
      askRafeeqBtn: "اسأل رفيق 💬"
    },
    en: {
      navTitle: "University of Jordan — Aqaba",
      navSubtitle: "Direct Student Academic Guide",
      heroTitle1: "Verified Answers,",
      heroTitle2: "Directly from Official University Sources",
      heroDesc: "Ask about faculties, instructors, the academic calendar, and deadlines — answers are retrieved directly from official UJ Aqaba portal pages.",
      heroCta: "Ask a Question",
      heroCalBtn: "📅 Academic Calendar 2026/2027",
      topicsTitle: "Frequently Asked Questions",
      consoleTitle: "Academic Advisor — Online Now",
      emptyTitle: "Welcome to UJ Aqaba Academic Guide",
      emptyDesc: "Select one of the frequent questions above, or type your query to receive verified answers from official UJ Aqaba portals.",
      inputPlaceholder: "Ask your academic question...",
      langBtnLabel: "العربية",
      studentLabel: "Student",
      botLabel: "Rafeeq — Academic Guide",
      citationText: "Official Source",
      errorMsg: "Sorry, a connection error occurred. Please try again later.",
      unavailableMsg: "This information is currently not available on the official portal.",
      stat1n: "6",
      stat1l: "Faculties Covered",
      stat2n: "AR / EN",
      stat2l: "Full Bilingual Support",
      stat3n: "Direct",
      stat3l: "From Official Portal",
      footerTitle: "University of Jordan — Aqaba",
      footerCopy: "© 2026 All Rights Reserved — IEEE Student Branch",
      footerCreator: "Designed & Developed by: <strong>Shahad Al-Rabaiah</strong>",
      sidebarToggleLabel: "Calendar & Menu",
      drawerTitle: "Aqaba Guide & Calendar",
      clockStatusTag: "Aqaba Local Time",
      drawerTabCal: "📅 Academic Calendar 2026/2027",
      drawerTabLinks: "🔗 Official Portals",
      drawerTabDeans: "🎓 College Deans",
      campusOpen: "Offices: Open Now (8AM - 3PM)",
      campusClosed: "Offices: Closed (Hours: 8AM - 3PM)",
      calBadgeTag: "Official Academic Calendar 2026 / 2027",
      calMainTitle: "Dates & Academic Calendar — University of Jordan Aqaba",
      calDesc: "Official dates approved by the University for the First Semester: Add/drop, examinations, and official holidays.",
      ftabAll: "All (28)",
      ftabReg: "Registration & Drop",
      ftabExam: "Exams & Grades",
      ftabHoliday: "Holidays & Breaks",
      ftabAcademic: "Academic Milestones",
      calSearchPlaceholder: "Search dates (exams, add/drop, holiday...)...",
      calThDate: "Date",
      calThDay: "Day",
      calThEvent: "Academic Event / Deadline",
      calThCat: "Category",
      calThAsk: "Inquire",
      askRafeeqBtn: "Ask Rafeeq 💬"
    }
  };

  const topicPrompts = {
    ar: [
      { prompt: "من عميد كلية نظم وتكنولوجيا المعلومات؟", label: "عمداء الكليات وجهات التواصل" },
      { prompt: "ما هو التقويم الأكاديمي للفصل الحالي ومواعيد السحب والإضافة؟", label: "التقويم الأكاديمي والسحب والإضافة" },
      { prompt: "أين يقع مكتب القبول والتسجيل وساعات المراجعة؟", label: "القبول والتسجيل وساعات المراجعة" },
      { prompt: "كيف يمكن تقديم طلب شكوى أو اقتراح إلكتروني؟", label: "تقديم شكوى أو اقتراح" },
      { prompt: "ما هي روابط بوابة التسجيل الذاتي للطلبة ومنصة التعلم الإلكتروني؟", label: "بوابة التسجيل ومنصة التعلم الإلكتروني" }
    ],
    en: [
      { prompt: "Who is the dean of the Faculty of Information Technology?", label: "Faculty Deans & Contacts" },
      { prompt: "What is the academic calendar and add/drop dates for the semester?", label: "Academic Calendar & Add/Drop" },
      { prompt: "Where is the Admission and Registration office and its working hours?", label: "Admission, Registration & Hours" },
      { prompt: "How can I submit an online complaint or suggestion?", label: "Submit a Complaint or Suggestion" },
      { prompt: "What are the student self-registration and e-learning portal links?", label: "Registration & E-Learning Portals" }
    ]
  };

  const MILESTONES_DATA = [
    {
      catClass: "tag-reg",
      icon: "🔄",
      tagAr: "سحب وإضافة",
      tagEn: "Add & Drop",
      titleAr: "فترة السحب والإضافة",
      titleEn: "Add/Drop Period",
      dateAr: "4 — 8 تشرين الأول 2026",
      dateEn: "4 — 8 October 2026",
      daysAr: "من الأحد إلى الخميس",
      daysEn: "Sunday to Thursday",
      promptAr: "متى موعد فترة السحب والإضافة للفصل الحالي؟",
      promptEn: "When is the add/drop period for the current semester?"
    },
    {
      catClass: "tag-academic",
      icon: "📚",
      tagAr: "بدء التدريس",
      tagEn: "Classes Begin",
      titleAr: "بدء التدريس في الفصل الأول",
      titleEn: "First Semester Classes Begin",
      dateAr: "11 تشرين الأول 2026",
      dateEn: "11 October 2026",
      daysAr: "يوم الأحد",
      daysEn: "Sunday",
      promptAr: "متى يبدأ التدريس في الفصل الأول؟",
      promptEn: "When do first semester classes begin?"
    },
    {
      catClass: "tag-exam",
      icon: "📝",
      tagAr: "امتحانات الميد",
      tagEn: "Midterm Exams",
      titleAr: "امتحانات منتصف الفصل الأول",
      titleEn: "First Semester Midterms",
      dateAr: "29 تشرين الثاني — 10 كانون الأول 2026",
      dateEn: "29 Nov — 10 Dec 2026",
      daysAr: "من الأحد إلى الخميس",
      daysEn: "Sunday to Thursday",
      promptAr: "متى امتحانات منتصف الفصل الأول؟",
      promptEn: "When are the first semester midterm exams?"
    },
    {
      catClass: "tag-exam",
      icon: "🎓",
      tagAr: "الامتحانات النهائية",
      tagEn: "Final Exams",
      titleAr: "الامتحانات النهائية للفصل الأول",
      titleEn: "First Semester Final Exams",
      dateAr: "17 — 28 كانون الثاني 2027",
      dateEn: "17 — 28 January 2027",
      daysAr: "من الأحد إلى الخميس",
      daysEn: "Sunday to Thursday",
      promptAr: "متى الامتحانات النهائية للفصل الأول؟",
      promptEn: "When are the first semester final exams?"
    },
    {
      catClass: "tag-holiday",
      icon: "🌴",
      tagAr: "عطلة رسمية",
      tagEn: "Official Holiday",
      titleAr: "إجازة ما بين الفصلين",
      titleEn: "Inter-Semester Break",
      dateAr: "31 كانون الثاني — 11 شباط 2027",
      dateEn: "31 Jan — 11 Feb 2027",
      daysAr: "من الأحد إلى الخميس",
      daysEn: "Sunday to Thursday",
      promptAr: "متى إجازة ما بين الفصلين للطلبة؟",
      promptEn: "When is the inter-semester break for students?"
    }
  ];

  const PORTALS_DATA = [
    {
      icon: "🏛️",
      url: "https://aqaba.ju.edu.jo",
      displayUrl: "aqaba.ju.edu.jo",
      nameAr: "بوابة فرع العقبة الرسمية",
      nameEn: "Official Aqaba Branch Portal"
    },
    {
      icon: "📝",
      url: "https://ujapps.ju.edu.jo/selfregappaq/",
      displayUrl: "ujapps.ju.edu.jo/selfregappaq",
      nameAr: "بوابة التسجيل الذاتي للطلبة",
      nameEn: "Student Self-Registration Portal"
    },
    {
      icon: "💻",
      url: "https://elearning.ju.edu.jo",
      displayUrl: "elearning.ju.edu.jo",
      nameAr: "منصة التعلم الإلكتروني المعتمدة",
      nameEn: "Official E-Learning Platform"
    },
    {
      icon: "📬",
      url: "https://eservices.ju.edu.jo/complaintsys/login.aspx",
      displayUrl: "eservices.ju.edu.jo",
      nameAr: "بوابة تقديم الشكاوى والاقتراحات",
      nameEn: "Complaints & Suggestions Portal"
    },
    {
      icon: "👨‍🏫",
      url: "https://aqaba.ju.edu.jo/ar/arabic/Pages/Academics.aspx",
      displayUrl: "Academics.aspx",
      nameAr: "دليل الكليات وأعضاء الهيئة التدريسية",
      nameEn: "Faculties & Academic Staff Directory"
    },
    {
      icon: "📋",
      url: "https://registration.ju.edu.jo",
      displayUrl: "registration.ju.edu.jo",
      nameAr: "وحدة القبول والتسجيل",
      nameEn: "Admission & Registration Unit"
    }
  ];

  const DEANS_DATA = [
    {
      collegeAr: "كلية تكنولوجيا المعلومات",
      collegeEn: "Faculty of Information Technology",
      deanAr: "د. سفيان الغزيوات",
      deanEn: "Dr. Sufyan Al-Ghazaiwat"
    },
    {
      collegeAr: "كلية إدارة الأعمال",
      collegeEn: "Faculty of Business",
      deanAr: "د. عمر سنجلاوي",
      deanEn: "Dr. Omar Sinjilawi"
    },
    {
      collegeAr: "كلية السياحة والفندقة",
      collegeEn: "Faculty of Tourism & Hospitality",
      deanAr: "د. عمر جوابرة",
      deanEn: "Dr. Omar Jawbrah"
    },
    {
      collegeAr: "كلية التمريض",
      collegeEn: "Faculty of Nursing",
      deanAr: "د. محمود الكلالدة",
      deanEn: "Dr. Mahmoud Al-Kalaldah"
    },
    {
      collegeAr: "كلية الأحياء",
      collegeEn: "Faculty of Biology",
      deanAr: "د. محمود الكلالدة",
      deanEn: "Dr. Mahmoud Al-Kalaldah"
    },
    {
      collegeAr: "كلية الرياضيات",
      collegeEn: "Faculty of Mathematics",
      deanAr: "د. محمود الكلالدة",
      deanEn: "Dr. Mahmoud Al-Kalaldah"
    },
    {
      collegeAr: "كلية اللغات",
      collegeEn: "Faculty of Languages",
      deanAr: "عمادة كلية اللغات",
      deanEn: "Deanship of Faculty of Languages"
    }
  ];

  const CALENDAR_EVENTS = [
    {
      cat: "reg",
      highlight: false,
      dateAr: "1-10-2026",
      dateEn: "1-10-2026",
      dayAr: "الخميس",
      dayEn: "Thursday",
      eventAr: "آخر موعد للمحاسبة على المواد المسجلة بدون غرامة، قبل إلغائها لعدم المحاسبة",
      eventEn: "Deadline for fee payment on registered courses without penalty, prior to cancellation for non-payment",
      tagAr: "تسديد الرسوم",
      tagEn: "Fee Payment",
      promptAr: "متى آخر موعد للمحاسبة على المواد المسجلة بدون غرامة؟",
      promptEn: "When is the deadline for course payment without fine?"
    },
    {
      cat: "exam",
      highlight: false,
      dateAr: "1-10-2026",
      dateEn: "1-10-2026",
      dayAr: "الخميس",
      dayEn: "Thursday",
      eventAr: "آخر موعد لتقديم طلب مراجعة علامة الامتحان النهائي لمواد الفصل الصيفي 2025/2026",
      eventEn: "Deadline to submit grade appeal requests for Summer Semester 2025/2026 final exams",
      tagAr: "مراجعة علامات",
      tagEn: "Grade Appeal",
      promptAr: "متى آخر موعد لمراجعة علامات الامتحان النهائي للفصل الصيفي؟",
      promptEn: "When is the deadline to appeal Summer semester final grades?"
    },
    {
      cat: "academic",
      highlight: false,
      dateAr: "4-10-2026",
      dateEn: "4-10-2026",
      dayAr: "الأحد",
      dayEn: "Sunday",
      eventAr: "بدء العام الجامعي 2026/2027 ودوام أعضاء الهيئة التدريسية",
      eventEn: "Start of Academic Year 2026/2027 and faculty members reporting to campus",
      tagAr: "بدء العام الجامعي",
      tagEn: "Academic Year Start",
      promptAr: "متى بدء العام الجامعي 2026/2027 ودوام الهيئة التدريسية؟",
      promptEn: "When does the academic year start for faculty members?"
    },
    {
      cat: "reg",
      highlight: true,
      dateAr: "4-8-10-2026",
      dateEn: "4-8 Oct 2026",
      dayAr: "الأحد — الخميس",
      dayEn: "Sunday — Thursday",
      eventAr: "🌟 فترة السحب والإضافة لمواد الفصل الأول 2026/2027",
      eventEn: "🌟 Add and Drop period for First Semester 2026/2027 courses",
      tagAr: "سحب وإضافة",
      tagEn: "Add & Drop",
      promptAr: "متى فترة السحب والإضافة للفصل الحالي وكيف أعدل جدولي؟",
      promptEn: "When is the Add/Drop period and how do I modify my schedule?"
    },
    {
      cat: "exam",
      highlight: false,
      dateAr: "8-10-2026",
      dateEn: "8-10-2026",
      dayAr: "الخميس",
      dayEn: "Thursday",
      eventAr: "آخر موعد لتقديم طلب التقدم للامتحان المئوي لمواد الفصل الصيفي 2025/2026 إلكترونياً",
      eventEn: "Online deadline to apply for comprehensive 100% exam for Summer Semester 2025/2026",
      tagAr: "امتحان مئوي",
      tagEn: "100% Exam",
      promptAr: "متى آخر موعد لتقديم طلب الامتحان المئوي؟",
      promptEn: "When is the deadline to apply for the 100% exam?"
    },
    {
      cat: "exam",
      highlight: false,
      dateAr: "8-10-2026",
      dateEn: "8-10-2026",
      dayAr: "الخميس",
      dayEn: "Thursday",
      eventAr: "آخر موعد لتقديم واعتماد أعذار التغيب عن الامتحانات النهائية لمواد الفصل الصيفي 2025/2026 إلكترونياً",
      eventEn: "Online deadline to submit and approve excuses for missing Summer 2025/2026 final exams",
      tagAr: "أعذار الامتحانات",
      tagEn: "Exam Excuses",
      promptAr: "متى آخر موعد لتقديم أعذار التغيب عن الامتحانات النهائية؟",
      promptEn: "When is the deadline to submit final exam absence excuses?"
    },
    {
      cat: "academic",
      highlight: true,
      dateAr: "11-10-2026",
      dateEn: "11-10-2026",
      dayAr: "الأحد",
      dayEn: "Sunday",
      eventAr: "🎓 بدء التدريس في الفصل الدراسي الأول 2026/2027",
      eventEn: "🎓 First Semester 2026/2027 classes begin",
      tagAr: "بدء التدريس",
      tagEn: "Classes Begin",
      promptAr: "متى بدء التدريس في الفصل الأول؟",
      promptEn: "When do classes begin for the first semester?"
    },
    {
      cat: "academic",
      highlight: false,
      dateAr: "11-15-10-2026",
      dateEn: "11-15 Oct 2026",
      dayAr: "الأحد — الخميس",
      dayEn: "Sunday — Thursday",
      eventAr: "أسبوع الإكتمال",
      eventEn: "Incomplete / Course Completion Resolution Week",
      tagAr: "أسبوع الإكتمال",
      tagEn: "Completion Week",
      promptAr: "ما هو موعد أسبوع الإكتمال في التقويم؟",
      promptEn: "When is the incomplete completion week?"
    },
    {
      cat: "academic",
      highlight: false,
      dateAr: "19-10-2026",
      dateEn: "19-10-2026",
      dayAr: "الاثنين",
      dayEn: "Monday",
      eventAr: "آخر موعد لتسليم نتائج مراجعة علامة الامتحان النهائي لمواد الفصل الصيفي 2025/2026 إلى وحدة القبول والتسجيل",
      eventEn: "Deadline to submit Summer 2025/2026 grade appeal results to Admission & Registration Unit",
      tagAr: "تدقيق نتائج",
      tagEn: "Result Audit",
      promptAr: "متى تسليم نتائج مراجعة علامات الصيفي للتسجيل؟",
      promptEn: "When must summer grade appeal results be submitted to registration?"
    },
    {
      cat: "academic",
      highlight: false,
      dateAr: "19-10-2026",
      dateEn: "19-10-2026",
      dayAr: "الاثنين",
      dayEn: "Monday",
      eventAr: "آخر موعد لاعتماد نتائج الامتحانات المئوية وترحيلها إلى وحدة القبول والتسجيل إلكترونياً",
      eventEn: "Deadline to approve and electronically transfer 100% exam results to Admission & Registration",
      tagAr: "ترحيل نتائج",
      tagEn: "Result Transfer",
      promptAr: "متى موعد اعتماد نتائج الامتحانات المئوية؟",
      promptEn: "When is the deadline to approve 100% exam results?"
    },
    {
      cat: "academic",
      highlight: false,
      dateAr: "19-10-2026",
      dateEn: "19-10-2026",
      dayAr: "الاثنين",
      dayEn: "Monday",
      eventAr: "آخر موعد لاعتماد نتائج الامتحانات التكميلية لمواد الفصل الصيفي 2025/2026 وترحيلها إلى وحدة القبول والتسجيل إلكترونياً",
      eventEn: "Deadline to approve and transfer makeup exam results for Summer 2025/2026 to Registration",
      tagAr: "امتحانات تكميلية",
      tagEn: "Makeup Exams",
      promptAr: "متى موعد اعتماد نتائج الامتحانات التكميلية للصيفي؟",
      promptEn: "When is the deadline to approve summer makeup exam results?"
    },
    {
      cat: "exam",
      highlight: true,
      dateAr: "29-11-2026 إلى 10-12-2026",
      dateEn: "29-11-2026 to 10-12-2026",
      dayAr: "الأحد — الخميس",
      dayEn: "Sunday — Thursday",
      eventAr: "📝 امتحانات منتصف الفصل الدراسي الأول 2026/2027",
      eventEn: "📝 First Semester 2026/2027 Midterm Examinations",
      tagAr: "امتحانات منتصف الفصل",
      tagEn: "Midterm Exams",
      promptAr: "متى مواعيد امتحانات منتصف الفصل الأول؟",
      promptEn: "When are the first semester midterm exam dates?"
    },
    {
      cat: "reg",
      highlight: false,
      dateAr: "13-12-2026 إلى 24-12-2026",
      dateEn: "13-12-2026 to 24-12-2026",
      dayAr: "الأحد — الخميس",
      dayEn: "Sunday — Thursday",
      eventAr: "فترة التسجيل على مواد الفصل الدراسي الثاني 2026/2027",
      eventEn: "Course registration period for Second Semester 2026/2027",
      tagAr: "تسجيل الفصل الثاني",
      tagEn: "Semester 2 Registration",
      promptAr: "متى موعد التسجيل لمواد الفصل الدراسي الثاني؟",
      promptEn: "When is registration for second semester courses?"
    },
    {
      cat: "holiday",
      highlight: false,
      dateAr: "25-12-2026",
      dateEn: "25-12-2026",
      dayAr: "الجمعة",
      dayEn: "Friday",
      eventAr: "🎄 عطلة عيد الميلاد المجيد",
      eventEn: "🎄 Christmas Holiday",
      tagAr: "عطلة رسمية",
      tagEn: "Official Holiday",
      promptAr: "متى عطلة عيد الميلاد المجيد بالجامعة؟",
      promptEn: "When is the university Christmas holiday?"
    },
    {
      cat: "holiday",
      highlight: false,
      dateAr: "1-1-2027",
      dateEn: "1-1-2027",
      dayAr: "الجمعة",
      dayEn: "Friday",
      eventAr: "🎉 عطلة رأس السنة الميلادية",
      eventEn: "🎉 New Year's Day Holiday",
      tagAr: "عطلة رسمية",
      tagEn: "Official Holiday",
      promptAr: "متى عطلة رأس السنة الميلادية؟",
      promptEn: "When is the New Year holiday?"
    },
    {
      cat: "reg",
      highlight: false,
      dateAr: "3-1-2027 إلى 3-2-2027",
      dateEn: "3-1-2027 to 3-2-2027",
      dayAr: "الأحد — الأربعاء",
      dayEn: "Sunday — Wednesday",
      eventAr: "فترة تقديم طلبات الانتقال من تخصص لآخر داخل الجامعة إلكترونياً",
      eventEn: "Online application period for internal major transfers within the university",
      tagAr: "انتقال تخصصات",
      tagEn: "Major Transfer",
      promptAr: "متى فترة تقديم طلبات الانتقال من تخصص لآخر؟",
      promptEn: "When is the internal major transfer application period?"
    },
    {
      cat: "academic",
      highlight: true,
      dateAr: "13-1-2027",
      dateEn: "13-1-2027",
      dayAr: "الأربعاء",
      dayEn: "Wednesday",
      eventAr: "📌 آخر يوم للتدريس في الفصل الأول 2026/2027",
      eventEn: "📌 Last day of classes for First Semester 2026/2027",
      tagAr: "نهاية التدريس",
      tagEn: "End of Classes",
      promptAr: "متى آخر يوم للتدريس في الفصل الأول؟",
      promptEn: "When is the last day of classes for the first semester?"
    },
    {
      cat: "academic",
      highlight: false,
      dateAr: "13-1-2027",
      dateEn: "13-1-2027",
      dayAr: "الأربعاء",
      dayEn: "Wednesday",
      eventAr: "آخر موعد لتسليم قوائم الحرمان إلى وحدة القبول والتسجيل",
      eventEn: "Deadline to submit attendance dismissal lists to Admission & Registration Unit",
      tagAr: "قوائم الحرمان",
      tagEn: "Dismissal Lists",
      promptAr: "متى آخر موعد لتسليم قوائم الحرمان للتسجيل؟",
      promptEn: "When is the deadline to submit attendance dismissal lists?"
    },
    {
      cat: "academic",
      highlight: false,
      dateAr: "13-1-2027",
      dateEn: "13-1-2027",
      dayAr: "الأربعاء",
      dayEn: "Wednesday",
      eventAr: "آخر موعد لاعتماد علامات الأعمال الفصلية وإعلانها للطلبة",
      eventEn: "Deadline to approve coursework grades and announce them to students",
      tagAr: "علامات الفصل",
      tagEn: "Coursework Grades",
      promptAr: "متى آخر موعد لاعتماد علامات الأعمال الفصلية؟",
      promptEn: "When is the deadline to approve coursework grades?"
    },
    {
      cat: "reg",
      highlight: false,
      dateAr: "14-1-2027",
      dateEn: "14-1-2027",
      dayAr: "الخميس",
      dayEn: "Thursday",
      eventAr: "آخر موعد للانسحاب من دراسة المواد أو من الفصل الأول",
      eventEn: "Deadline for course withdrawal or complete semester withdrawal",
      tagAr: "انسحاب من المواد",
      tagEn: "Course Withdrawal",
      promptAr: "متى آخر موعد للانسحاب من دراسة مادة أو من الفصل؟",
      promptEn: "When is the course withdrawal deadline?"
    },
    {
      cat: "reg",
      highlight: false,
      dateAr: "14-1-2027",
      dateEn: "14-1-2027",
      dayAr: "الخميس",
      dayEn: "Thursday",
      eventAr: "آخر موعد للانسحاب من الجامعة لطلبة البكالوريوس المسجلين في الفصل الحالي",
      eventEn: "Deadline for enrolled undergraduate students to withdraw from the university",
      tagAr: "انسحاب من الجامعة",
      tagEn: "University Withdrawal",
      promptAr: "متى آخر موعد للانسحاب من الجامعة لطلبة البكالوريوس؟",
      promptEn: "When is the deadline to withdraw from the university for undergraduates?"
    },
    {
      cat: "exam",
      highlight: true,
      dateAr: "17-1-2027 إلى 28-1-2027",
      dateEn: "17-1-2027 to 28-1-2027",
      dayAr: "الأحد — الخميس",
      dayEn: "Sunday — Thursday",
      eventAr: "🧑‍🎓 الامتحانات النهائية للفصل الأول 2026/2027",
      eventEn: "🧑‍🎓 First Semester 2026/2027 Final Examinations",
      tagAr: "امتحانات نهائية",
      tagEn: "Final Exams",
      promptAr: "متى موعد الامتحانات النهائية للفصل الأول؟",
      promptEn: "When are the first semester final exams?"
    },
    {
      cat: "holiday",
      highlight: true,
      dateAr: "31-1-2027 إلى 11-2-2027",
      dateEn: "31-1-2027 to 11-2-2027",
      dayAr: "الأحد — الخميس",
      dayEn: "Sunday — Thursday",
      eventAr: "🌴 إجازة ما بين الفصلين للطلبة",
      eventEn: "🌴 Inter-Semester Break for Students",
      tagAr: "إجازة بين الفصلين",
      tagEn: "Inter-Semester Break",
      promptAr: "متى إجازة ما بين الفصلين للطلبة؟",
      promptEn: "When is the student inter-semester break?"
    },
    {
      cat: "academic",
      highlight: false,
      dateAr: "31-1-2027",
      dateEn: "31-1-2027",
      dayAr: "الأحد",
      dayEn: "Sunday",
      eventAr: "آخر موعد لتسليم عضو هيئة التدريس نتائج الامتحانات إلى الكلية (الساعة 1:00 ظهراً)",
      eventEn: "Faculty deadline to submit final examination results to the Deanship (1:00 PM)",
      tagAr: "تسليم العلامات",
      tagEn: "Grade Submission",
      promptAr: "متى موعد تسليم نتائج الامتحانات النهائية إلى الكلية؟",
      promptEn: "When must faculty submit final exam grades to the college?"
    },
    {
      cat: "academic",
      highlight: false,
      dateAr: "1-2-2027",
      dateEn: "1-2-2027",
      dayAr: "الاثنين",
      dayEn: "Monday",
      eventAr: "آخر موعد لتسليم نتائج امتحانات الفصل الأول 2026/2027 إلى وحدة القبول والتسجيل (الساعة 1:00 ظهراً)",
      eventEn: "Deadline to submit First Semester 2026/2027 exam results to Admission & Registration (1:00 PM)",
      tagAr: "تسليم للتسجيل",
      tagEn: "Registration Delivery",
      promptAr: "متى آخر موعد لتسليم نتائج الامتحانات لوحدة القبول والتسجيل؟",
      promptEn: "When must exam results be delivered to Admission & Registration?"
    },
    {
      cat: "academic",
      highlight: false,
      dateAr: "1-2-2027",
      dateEn: "1-2-2027",
      dayAr: "الاثنين",
      dayEn: "Monday",
      eventAr: "آخر موعد لتقديم تنسيب مجالس الكليات بمنح الدرجات العلمية والشهادات إلى مجلس العمداء",
      eventEn: "Deadline for College Councils to submit graduation degree recommendations to Deans Council",
      tagAr: "تنسيب درجات",
      tagEn: "Degree Recommendation",
      promptAr: "متى موعد تنسيب مجالس الكليات بمنح الدرجات العلمية؟",
      promptEn: "When is the deadline for college councils' graduation recommendations?"
    },
    {
      cat: "holiday",
      highlight: false,
      dateAr: "2-2-2027",
      dateEn: "2-2-2027",
      dayAr: "الثلاثاء",
      dayEn: "Tuesday",
      eventAr: "بدء الإجازة السنوية لمدة أسبوع لأعضاء الهيئة التدريسية",
      eventEn: "Start of one-week annual leave for faculty teaching members",
      tagAr: "إجازة تدريسية",
      tagEn: "Faculty Leave",
      promptAr: "متى تبدأ الإجازة السنوية لأعضاء الهيئة التدريسية؟",
      promptEn: "When does the faculty annual leave start?"
    },
    {
      cat: "academic",
      highlight: true,
      dateAr: "3-2-2027",
      dateEn: "3-2-2027",
      dayAr: "الأربعاء",
      dayEn: "Wednesday",
      eventAr: "🎓 قرار مجلس العمداء بمنح الدرجات العلمية والشهادات",
      eventEn: "🎓 Deans Council formal resolution granting degrees and graduation certificates",
      tagAr: "قرار العمداء وتخريج",
      tagEn: "Deans Decision",
      promptAr: "متى موعد صدور قرار مجلس العمداء بمنح الدرجات العلمية والشهادات؟",
      promptEn: "When is the Deans Council decision on conferring degrees issued?"
    }
  ];

  function applyTheme(theme) {
    currentTheme = theme;
    htmlDoc.setAttribute("data-theme", theme);
    localStorage.setItem("uj_theme", theme);
    if (theme === "dark") {
      themeIconSun.classList.add("hidden");
      themeIconMoon.classList.remove("hidden");
    } else {
      themeIconSun.classList.remove("hidden");
      themeIconMoon.classList.add("hidden");
    }
  }

  function renderMilestones(lang) {
    if (!milestonesGrid) return;
    const askText = i18n[lang].askRafeeqBtn;
    milestonesGrid.innerHTML = MILESTONES_DATA.map((m, idx) => {
      const activeClass = idx === 0 ? " active-card" : "";
      const tagText = lang === "ar" ? m.tagAr : m.tagEn;
      const titleText = lang === "ar" ? m.titleAr : m.titleEn;
      const dateText = lang === "ar" ? m.dateAr : m.dateEn;
      const daysText = lang === "ar" ? m.daysAr : m.daysEn;
      const promptText = lang === "ar" ? m.promptAr : m.promptEn;

      return `
        <div class="milestone-card${activeClass}" data-prompt="${promptText}">
          <div class="milestone-pill ${m.catClass}">${tagText}</div>
          <div class="milestone-icon-wrap">${m.icon}</div>
          <h3 class="milestone-title">${titleText}</h3>
          <p class="milestone-date">${dateText}</p>
          <p class="milestone-days">${daysText}</p>
          <button class="milestone-ask-btn">${askText}</button>
        </div>
      `;
    }).join("");

    milestonesGrid.querySelectorAll(".milestone-card").forEach(card => {
      card.addEventListener("click", () => {
        const prompt = card.getAttribute("data-prompt");
        if (prompt) {
          closeDrawer();
          document.getElementById("console").scrollIntoView({ behavior: "smooth", block: "start" });
          handleSend(prompt);
        }
      });
    });
  }

  function renderPortals(lang) {
    if (!drawerLinksGrid) return;
    drawerLinksGrid.innerHTML = PORTALS_DATA.map(p => {
      const nameText = lang === "ar" ? p.nameAr : p.nameEn;
      return `
        <a href="${p.url}" target="_blank" rel="noopener noreferrer" class="drawer-link-card">
          <span class="dl-icon">${p.icon}</span>
          <div class="dl-info">
            <strong class="dl-name">${nameText}</strong>
            <small class="dl-url">${p.displayUrl}</small>
          </div>
          <span class="dl-arrow">↗</span>
        </a>
      `;
    }).join("");
  }

  function renderDeans(lang) {
    if (!drawerDeansList) return;
    drawerDeansList.innerHTML = DEANS_DATA.map(d => {
      const collegeText = lang === "ar" ? d.collegeAr : d.collegeEn;
      const deanText = lang === "ar" ? d.deanAr : d.deanEn;
      return `<li><strong>${collegeText}:</strong> ${deanText}</li>`;
    }).join("");
  }

  function renderCalendarTable(lang) {
    if (!calendarTableBody) return;
    const askText = i18n[lang].askRafeeqBtn;

    calendarTableBody.innerHTML = CALENDAR_EVENTS.map(ev => {
      const dateText = lang === "ar" ? ev.dateAr : ev.dateEn;
      const dayText = lang === "ar" ? ev.dayAr : ev.dayEn;
      const eventText = lang === "ar" ? ev.eventAr : ev.eventEn;
      const tagText = lang === "ar" ? ev.tagAr : ev.tagEn;
      const promptText = lang === "ar" ? ev.promptAr : ev.promptEn;
      const rowClass = ev.highlight ? ' class="highlight-row"' : "";
      const fontBold = ev.highlight ? " font-bold" : "";

      return `
        <tr data-cat="${ev.cat}"${rowClass}>
          <td><span class="cal-date-badge${fontBold}">${dateText}</span></td>
          <td><span class="cal-day">${dayText}</span></td>
          <td class="cal-event-text${fontBold}">${eventText}</td>
          <td><span class="cal-tag tag-${ev.cat}">${tagText}</span></td>
          <td><button class="cal-ask-btn" data-prompt="${promptText}">${askText}</button></td>
        </tr>
      `;
    }).join("");

    calendarTableBody.querySelectorAll(".cal-ask-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const prompt = btn.getAttribute("data-prompt");
        if (prompt) {
          closeDrawer();
          document.getElementById("console").scrollIntoView({ behavior: "smooth", block: "start" });
          handleSend(prompt);
        }
      });
    });

    filterCalendarRows();
  }

  function filterCalendarRows() {
    const query = currentSearchQuery.toLowerCase().trim();
    const rows = calendarTableBody ? calendarTableBody.querySelectorAll("tr") : [];
    rows.forEach(row => {
      const rowCat = row.getAttribute("data-cat");
      const rowText = row.innerText.toLowerCase();

      const matchesCat = (currentCategory === "all" || rowCat === currentCategory);
      const matchesSearch = !query || rowText.includes(query);

      if (matchesCat && matchesSearch) {
        row.style.display = "";
      } else {
        row.style.display = "none";
      }
    });
  }

  function applyLang(lang) {
    currentLang = lang;
    htmlDoc.setAttribute("lang", lang);
    htmlDoc.setAttribute("dir", lang === "ar" ? "rtl" : "ltr");
    localStorage.setItem("uj_lang", lang);

    const t = i18n[lang];

    // Navbar
    if (navTitle) navTitle.textContent = t.navTitle;
    if (navSubtitle) navSubtitle.textContent = t.navSubtitle;
    if (sidebarToggleLabel) sidebarToggleLabel.textContent = t.sidebarToggleLabel;
    if (langLabel) langLabel.textContent = t.langBtnLabel;

    // Hero Section
    if (heroTitle1) heroTitle1.textContent = t.heroTitle1;
    if (heroTitle2) heroTitle2.textContent = t.heroTitle2;
    if (heroDesc) heroDesc.textContent = t.heroDesc;
    if (heroCta && heroCta.querySelector("span")) heroCta.querySelector("span").textContent = t.heroCta;
    if (heroCalendarCta && heroCalendarCta.querySelector("span")) heroCalendarCta.querySelector("span").textContent = t.heroCalBtn;

    // Stats
    if (stat1n) stat1n.textContent = t.stat1n;
    if (stat1l) stat1l.textContent = t.stat1l;
    if (stat2n) stat2n.textContent = t.stat2n;
    if (stat2l) stat2l.textContent = t.stat2l;
    if (stat3n) stat3n.textContent = t.stat3n;
    if (stat3l) stat3l.textContent = t.stat3l;

    // Topics (FAQ)
    if (topicsTitle) topicsTitle.textContent = t.topicsTitle;
    topicCards.forEach((card, i) => {
      const p = topicPrompts[lang][i];
      if (p) {
        card.setAttribute("data-prompt", p.prompt);
        const span = card.querySelector("span");
        if (span) span.textContent = p.label;
      }
    });

    // Console & Input
    if (consoleTitle) consoleTitle.textContent = t.consoleTitle;
    if (emptyTitle) emptyTitle.textContent = t.emptyTitle;
    if (emptyDesc) emptyDesc.textContent = t.emptyDesc;
    if (userInput) userInput.placeholder = t.inputPlaceholder;

    // Footer
    if (footerTitle) footerTitle.textContent = t.footerTitle;
    if (footerCopy) footerCopy.textContent = t.footerCopy;
    if (footerCreator) footerCreator.innerHTML = t.footerCreator;

    // Drawer Header & Tabs
    if (drawerTitle) drawerTitle.textContent = t.drawerTitle;
    if (clockStatusTag) clockStatusTag.textContent = t.clockStatusTag;
    if (drawerTabCalBtn && drawerTabCalBtn.querySelector("span")) drawerTabCalBtn.querySelector("span").textContent = t.drawerTabCal;
    if (drawerTabLinksBtn && drawerTabLinksBtn.querySelector("span")) drawerTabLinksBtn.querySelector("span").textContent = t.drawerTabLinks;
    if (drawerTabDeansBtn && drawerTabDeansBtn.querySelector("span")) drawerTabDeansBtn.querySelector("span").textContent = t.drawerTabDeans;

    // Calendar Header
    if (calBadgeTag) calBadgeTag.innerHTML = `<span class="badge-dot"></span> ${t.calBadgeTag}`;
    if (calMainTitle) calMainTitle.textContent = t.calMainTitle;
    if (calDesc) calDesc.textContent = t.calDesc;

    // Calendar Filter Tabs
    if (ftabAll) ftabAll.textContent = t.ftabAll;
    if (ftabReg) ftabReg.textContent = t.ftabReg;
    if (ftabExam) ftabExam.textContent = t.ftabExam;
    if (ftabHoliday) ftabHoliday.textContent = t.ftabHoliday;
    if (ftabAcademic) ftabAcademic.textContent = t.ftabAcademic;

    // Calendar Search Placeholder
    if (calSearchInput) calSearchInput.placeholder = t.calSearchPlaceholder;

    // Calendar Table Headers
    if (calThDate) calThDate.textContent = t.calThDate;
    if (calThDay) calThDay.textContent = t.calThDay;
    if (calThEvent) calThEvent.textContent = t.calThEvent;
    if (calThCat) calThCat.textContent = t.calThCat;
    if (calThAsk) calThAsk.textContent = t.calThAsk;

    // Dynamic Renderers
    renderMilestones(lang);
    renderPortals(lang);
    renderDeans(lang);
    renderCalendarTable(lang);
    updateLiveClock();
  }

  themeBtn.addEventListener("click", () => applyTheme(currentTheme === "dark" ? "light" : "dark"));
  langBtn.addEventListener("click", () => applyLang(currentLang === "ar" ? "en" : "ar"));

  // Initial Theme & Language Application
  applyTheme(currentTheme);
  applyLang(currentLang);

  // User input handling
  userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = `${Math.min(userInput.scrollHeight, 120)}px`;
  });

  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  sendBtn.addEventListener("click", () => handleSend());

  topicCards.forEach(card => {
    card.addEventListener("click", () => {
      const promptText = card.getAttribute("data-prompt");
      if (promptText) {
        document.getElementById("console").scrollIntoView({ behavior: "smooth", block: "start" });
        handleSend(promptText);
      }
    });
  });

  // Drawer Controls
  function openDrawer() {
    if (!sideDrawer) return;
    sideDrawer.classList.add("open");
    if (drawerBackdrop) drawerBackdrop.classList.remove("hidden");
    document.body.style.overflow = "hidden";
  }

  function closeDrawer() {
    if (!sideDrawer) return;
    sideDrawer.classList.remove("open");
    if (drawerBackdrop) drawerBackdrop.classList.add("hidden");
    document.body.style.overflow = "";
  }

  if (sidebarToggleBtn) sidebarToggleBtn.addEventListener("click", openDrawer);
  if (drawerCloseBtn) drawerCloseBtn.addEventListener("click", closeDrawer);
  if (drawerBackdrop) drawerBackdrop.addEventListener("click", closeDrawer);
  if (heroCalendarCta) {
    heroCalendarCta.addEventListener("click", (e) => {
      e.preventDefault();
      openDrawer();
      if (drawerTabCalBtn) drawerTabCalBtn.click();
    });
  }

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && sideDrawer && sideDrawer.classList.contains("open")) {
      closeDrawer();
    }
  });

  // Drawer Tab Switcher
  function switchDrawerTab(targetTab) {
    [drawerTabCalBtn, drawerTabLinksBtn, drawerTabDeansBtn].forEach(btn => {
      if (btn) btn.classList.remove("active");
    });
    [drawerCalView, drawerLinksView, drawerDeansView].forEach(view => {
      if (view) view.classList.add("hidden");
    });

    if (targetTab === "calendar" && drawerTabCalBtn && drawerCalView) {
      drawerTabCalBtn.classList.add("active");
      drawerCalView.classList.remove("hidden");
    } else if (targetTab === "links" && drawerTabLinksBtn && drawerLinksView) {
      drawerTabLinksBtn.classList.add("active");
      drawerLinksView.classList.remove("hidden");
    } else if (targetTab === "deans" && drawerTabDeansBtn && drawerDeansView) {
      drawerTabDeansBtn.classList.add("active");
      drawerDeansView.classList.remove("hidden");
    }
  }

  if (drawerTabCalBtn) drawerTabCalBtn.addEventListener("click", () => switchDrawerTab("calendar"));
  if (drawerTabLinksBtn) drawerTabLinksBtn.addEventListener("click", () => switchDrawerTab("links"));
  if (drawerTabDeansBtn) drawerTabDeansBtn.addEventListener("click", () => switchDrawerTab("deans"));

  // Live Time / Clock & Office Hours Status
  function updateLiveClock() {
    if (!liveClockElem) return;

    try {
      const now = new Date();
      const timeFormatter = new Intl.DateTimeFormat(currentLang === "ar" ? "ar-JO" : "en-US", {
        timeZone: "Asia/Amman",
        hour: "numeric",
        minute: "2-digit",
        second: "2-digit",
        hour12: true
      });
      liveClockElem.textContent = timeFormatter.format(now);

      const dateFormatter = new Intl.DateTimeFormat(currentLang === "ar" ? "ar-JO" : "en-US", {
        timeZone: "Asia/Amman",
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric"
      });
      if (liveDateElem) liveDateElem.textContent = dateFormatter.format(now);

      const jordanHourStr = new Intl.DateTimeFormat("en-US", {
        timeZone: "Asia/Amman",
        hour: "numeric",
        hour12: false
      }).format(now);
      const jordanDayStr = new Intl.DateTimeFormat("en-US", {
        timeZone: "Asia/Amman",
        weekday: "short"
      }).format(now);

      const hourNum = parseInt(jordanHourStr, 10);
      const isWorkingDay = ["Sun", "Mon", "Tue", "Wed", "Thu"].includes(jordanDayStr);
      const isOpen = isWorkingDay && (hourNum >= 8 && hourNum < 15);

      const t = i18n[currentLang] || i18n.ar;
      if (campusStatusPill) {
        if (isOpen) {
          campusStatusPill.className = "campus-pill pill-open";
          campusStatusPill.textContent = t.campusOpen;
        } else {
          campusStatusPill.className = "campus-pill pill-closed";
          campusStatusPill.textContent = t.campusClosed;
        }
      }
    } catch (e) {
      console.warn("Clock formatting error:", e);
    }
  }

  updateLiveClock();
  setInterval(updateLiveClock, 1000);

  // Calendar Category Filters
  const calFilterTabs = [ftabAll, ftabReg, ftabExam, ftabHoliday, ftabAcademic].filter(Boolean);
  calFilterTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      calFilterTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      currentCategory = tab.getAttribute("data-category") || "all";
      filterCalendarRows();
    });
  });

  // Calendar Live Search
  if (calSearchInput) {
    calSearchInput.addEventListener("input", (e) => {
      currentSearchQuery = e.target.value;
      filterCalendarRows();
    });
  }

  function parseMarkdown(text) {
    if (!text) return "";
    let html = text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');

    let lines = html.split("\n");
    let inList = false;
    let result = [];

    lines.forEach(line => {
      let trimmed = line.trim();
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ") || trimmed.startsWith("• ")) {
        if (!inList) { result.push("<ul>"); inList = true; }
        const itemContent = trimmed.replace(/^[-*•]\s*/, "");
        result.push(`<li>${itemContent}</li>`);
      } else {
        if (inList) { result.push("</ul>"); inList = false; }
        if (trimmed) result.push(`<p>${trimmed}</p>`);
      }
    });
    if (inList) result.push("</ul>");
    return result.join("");
  }

  async function handleSend(customText) {
    const text = (customText || userInput.value).trim();
    if (!text || isLoading) return;

    if (emptyState) emptyState.style.display = "none";

    appendMessage({
      sender: "user",
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });

    if (!customText) {
      userInput.value = "";
      userInput.style.height = "auto";
    }

    isLoading = true;
    sendBtn.disabled = true;
    const typingElem = showTypingIndicator();

    try {
      const res = await fetch(`${API_BASE_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          prompt: text,
          session_id: sessionId,
          language: currentLang,
          lang: currentLang
        })
      });

      const data = await res.json();
      removeTypingIndicator(typingElem);

      const replyText = data.reply || data.answer || i18n[currentLang].unavailableMsg;
      // Strict Conditional Source: NEVER show official source on greetings, life updates, or refusals
      const sourceUrl = data.source_url || (data.sources && data.sources.length > 0 ? data.sources[0]?.url : null);

      appendMessage({
        sender: "bot",
        text: replyText,
        source_url: sourceUrl,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });

    } catch (err) {
      console.error("API error:", err);
      removeTypingIndicator(typingElem);
      appendMessage({
        sender: "bot",
        text: i18n[currentLang].errorMsg,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });
    } finally {
      isLoading = false;
      sendBtn.disabled = false;
    }
  }

  function appendMessage(msg) {
    const wrapper = document.createElement("div");
    wrapper.className = `msg-wrapper ${msg.sender}`;

    const meta = document.createElement("div");
    meta.className = "msg-meta";
    const senderName = msg.sender === "user" ? i18n[currentLang].studentLabel : i18n[currentLang].botLabel;
    meta.innerHTML = `<span>${senderName}</span> • <span>${msg.timestamp}</span>`;

    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";
    bubble.innerHTML = parseMarkdown(msg.text);

    // Only render source badge when source_url is explicitly provided and non-null
    if (msg.sender === "bot" && msg.source_url) {
      const citationDiv = document.createElement("div");
      citationDiv.className = "citation-badge";
      const link = document.createElement("a");
      link.className = "citation-link";
      link.href = msg.source_url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.innerHTML = `
        <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
          <polyline points="15 3 21 3 21 9"></polyline>
          <line x1="10" y1="14" x2="21" y2="3"></line>
        </svg>
        <span>${i18n[currentLang].citationText}</span>
      `;
      citationDiv.appendChild(link);
      bubble.appendChild(citationDiv);
    }

    wrapper.appendChild(meta);
    wrapper.appendChild(bubble);
    chatStream.appendChild(wrapper);
    chatStream.scrollTop = chatStream.scrollHeight;
  }

  function showTypingIndicator() {
    const indicator = document.createElement("div");
    indicator.className = "msg-wrapper bot";
    indicator.innerHTML = `
      <div class="typing-indicator">
        <div class="dot"></div><div class="dot"></div><div class="dot"></div>
      </div>
    `;
    chatStream.appendChild(indicator);
    chatStream.scrollTop = chatStream.scrollHeight;
    return indicator;
  }

  function removeTypingIndicator(elem) {
    if (elem && elem.parentNode) elem.parentNode.removeChild(elem);
  }

});
