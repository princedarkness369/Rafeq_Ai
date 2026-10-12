document.addEventListener("DOMContentLoaded", () => {
  const htmlDoc = document.documentElement;
  const themeBtn = document.getElementById("theme-btn");
  const themeIconSun = document.getElementById("theme-icon-sun");
  const themeIconMoon = document.getElementById("theme-icon-moon");

  const langBtn = document.getElementById("lang-btn");
  const langLabel = document.getElementById("lang-label");

  const navTitle = document.getElementById("nav-title");
  const navSubtitle = document.getElementById("nav-subtitle");

  const heroDesc = document.getElementById("hero-desc");
  const heroCta = document.getElementById("hero-cta").querySelector("span");
  const topicsTitle = document.getElementById("topics-title");
  const consoleTitle = document.getElementById("console-title");

  const emptyState = document.getElementById("empty-state");
  const emptyTitle = document.getElementById("empty-title");
  const emptyDesc = document.getElementById("empty-desc");

  const stat1l = document.getElementById("stat1-l");
  const stat2n = document.getElementById("stat2-n");
  const stat2l = document.getElementById("stat2-l");
  const stat3n = document.getElementById("stat3-n");
  const stat3l = document.getElementById("stat3-l");

  const footerTitle = document.getElementById("footer-title");

  const chatStream = document.getElementById("chat-stream");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const topicCards = document.querySelectorAll(".topic-card");

  let currentTheme = localStorage.getItem("uj_theme") || "light";
  let currentLang = localStorage.getItem("uj_lang") || "ar";
  let sessionId = `session_${Date.now()}`;
  let isLoading = false;

  const i18n = {
    ar: {
      navTitle: "الجامعة الأردنية — فرع العقبة",
      navSubtitle: "دليل الطالب الأكاديمي المباشر",
      heroDesc: "اسأل عن الكليات، أعضاء الهيئة التدريسية، التقويم الأكاديمي، والمواعيد — والدليل يستخرج الجواب مباشرة من صفحات بوابة الجامعة الأردنية فرع العقبة.",
      heroCta: "ابدأ السؤال",
      topicsTitle: "استكشف بسرعة",
      consoleTitle: "المرشد الأكاديمي — متصل الآن",
      emptyTitle: "أهلاً بك في دليل الجامعة الأردنية الأكاديمي",
      emptyDesc: "اختر أحد المواضيع أعلاه، أو اكتب سؤالك للحصول على إجابة موثقة من صفحات بوابة الجامعة الأردنية فرع العقبة.",
      inputPlaceholder: "اكتب سؤالك الأكاديمي...",
      langBtnLabel: "English",
      studentLabel: "الطالب",
      botLabel: "دليل الجامعة الأردنية",
      citationText: "المصدر الرسمي",
      errorMsg: "عذراً، حدث خطأ في الاتصال بالخادم الرئيسي. يرجى المحاولة لاحقاً.",
      unavailableMsg: "عذراً، هذه المعلومة غير متوفرة حالياً على صفحات البوابة الرسمية.",
      stat1l: "كليات مغطّاة",
      stat2n: "عربي / إنجليزي",
      stat2l: "دعم كامل بلغتين",
      stat3n: "مباشر",
      stat3l: "من البوابة الرسمية",
      footerTitle: "الجامعة الأردنية — فرع العقبة"
    },
    en: {
      navTitle: "University of Jordan — Aqaba",
      navSubtitle: "Direct Student Academic Guide",
      heroDesc: "Ask about faculties, instructors, the academic calendar, and deadlines — answers are pulled directly from the UJ Aqaba portal.",
      heroCta: "Ask a question",
      topicsTitle: "Explore quickly",
      consoleTitle: "Academic guide — online now",
      emptyTitle: "Welcome to the UJ Aqaba academic guide",
      emptyDesc: "Pick a topic above, or type your question to get a verified answer sourced from the UJ Aqaba portal.",
      inputPlaceholder: "Ask your academic question...",
      langBtnLabel: "العربية",
      studentLabel: "Student",
      botLabel: "UJ Guide",
      citationText: "Official source",
      errorMsg: "Sorry, a connection error occurred. Please try again later.",
      unavailableMsg: "This information isn't available on the official portal yet.",
      stat1l: "faculties covered",
      stat2n: "AR / EN",
      stat2l: "full bilingual support",
      stat3n: "Live",
      stat3l: "from the official portal",
      footerTitle: "University of Jordan — Aqaba"
    }
  };

  const topicPrompts = {
    ar: [
      "من عميد كلية نظم وتكنولوجيا المعلومات؟",
      "ما هو التقويم الأكاديمي للفصل الحالي ومواعيد السحب والإضافة؟",
      "أين يقع مكتب القبول والتسجيل وساعات المراجعة؟",
      "كيف يمكن تقديم طلب شكوى أو اقتراح إلكتروني؟",
      "ما هي روابط بوابة التسجيل الذاتي RegApp وبوابة التعليم الإلكتروني؟"
    ],
    en: [
      "Who is the dean of the Faculty of IT?",
      "What is the current academic calendar and add/drop dates?",
      "Where is the admissions and registration office and its office hours?",
      "How can I submit a complaint or suggestion online?",
      "What are the RegApp self-registration and e-learning portal links?"
    ]
  };

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

  function applyLang(lang) {
    currentLang = lang;
    htmlDoc.setAttribute("lang", lang);
    htmlDoc.setAttribute("dir", lang === "ar" ? "rtl" : "ltr");
    localStorage.setItem("uj_lang", lang);

    const t = i18n[lang];
    navTitle.textContent = t.navTitle;
    navSubtitle.textContent = t.navSubtitle;
    heroDesc.textContent = t.heroDesc;
    heroCta.textContent = t.heroCta;
    topicsTitle.textContent = t.topicsTitle;
    consoleTitle.textContent = t.consoleTitle;
    emptyTitle.textContent = t.emptyTitle;
    emptyDesc.textContent = t.emptyDesc;
    userInput.placeholder = t.inputPlaceholder;
    langLabel.textContent = t.langBtnLabel;
    stat1l.textContent = t.stat1l;
    stat2n.textContent = t.stat2n;
    stat2l.textContent = t.stat2l;
    stat3n.textContent = t.stat3n;
    stat3l.textContent = t.stat3l;
    footerTitle.textContent = t.footerTitle;

    topicCards.forEach((card, i) => {
      card.setAttribute("data-prompt", topicPrompts[lang][i]);
      card.querySelector("span").textContent = card.querySelector("span").textContent;
    });
  }

  themeBtn.addEventListener("click", () => applyTheme(currentTheme === "dark" ? "light" : "dark"));
  langBtn.addEventListener("click", () => applyLang(currentLang === "ar" ? "en" : "ar"));

  applyTheme(currentTheme);
  applyLang(currentLang);

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
      if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
        if (!inList) { result.push("<ul>"); inList = true; }
        result.push(`<li>${trimmed.substring(2)}</li>`);
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
      const res = await fetch("http://localhost:8000/api/chat", {
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
      const sourceUrl = data.source_url || (data.sources && data.sources[0]?.url) || "https://aqaba.ju.edu.jo";

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
