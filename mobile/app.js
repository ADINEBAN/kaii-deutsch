/**
 * WordFeather Mobile Application Logic
 * Engineered for Realme GT Neo 2T (120Hz AMOLED, Liquid Glass UX)
 */

(function () {
  'use strict';

  // State Management
  const state = {
    currentTab: 'dict',
    currentLevel: 'ALL',
    currentFilterPos: 'ALL',
    searchQuery: '',
    
    // Data stores
    words: [],
    wordsFiltered: [],
    conjugations: {},
    sentences: {},
    grammar: {},
    
    // Pagination for 120Hz smooth scrolling
    page: 1,
    pageSize: 30,
    
    // Active themes filter
    selectedCategory: null,
    
    // Sätze letter filter
    selectedLetter: 'ALL',
    
    // Practice state ('flashcard' | 'match' | 'quiz-de-vi' | 'quiz-vi-de')
    practiceMode: 'flashcard',
    flashcardList: [],
    flashcardIndex: 0,
    flashcardFlipped: false,
    flashcardScore: { known: 0, total: 0 },
    
    // Match game state
    matchTiles: [],
    matchSelectedTile: null,
    matchPairsCount: 6,
    matchPairsFound: 0,
    matchTries: 0,
    matchLocked: false,

    // Quiz DE -> VI
    quizQuestions: [],
    quizIndex: 0,
    quizScore: 0,

    // Quiz VI -> DE
    quizViDeQuestions: [],
    quizViDeIndex: 0,
    quizViDeScore: 0,
    
    // TTS Audio state
    isTtsOnline: false,
    audioCache: new Map(),
    currentAudio: null
  };

  // DOM Elements cache
  const el = {};

  // Category Icon Mapping (Monochrome Line Icons via Iconify)
  const CATEGORY_ICONS = {
    // 39 Active categories from words_final.json
    'Allgemein': '<iconify-icon icon="lucide:book-open" width="22" height="22"></iconify-icon>',
    'Arbeit & Beruf': '<iconify-icon icon="lucide:briefcase" width="22" height="22"></iconify-icon>',
    'Argumentation & Analyse': '<iconify-icon icon="lucide:scale" width="22" height="22"></iconify-icon>',
    'Verkehr & Reisen': '<iconify-icon icon="lucide:compass" width="22" height="22"></iconify-icon>',
    'Schule & Bildung': '<iconify-icon icon="lucide:graduation-cap" width="22" height="22"></iconify-icon>',
    'Koerper & Gesundheit': '<iconify-icon icon="lucide:activity" width="22" height="22"></iconify-icon>',
    'Recht & Politik': '<iconify-icon icon="lucide:landmark" width="22" height="22"></iconify-icon>',
    'Gesellschaft & Umwelt': '<iconify-icon icon="lucide:sun" width="22" height="22"></iconify-icon>',
    'Gefuehle & Charakter': '<iconify-icon icon="lucide:heart" width="22" height="22"></iconify-icon>',
    'Kommunikation & Sprache': '<iconify-icon icon="lucide:message-square" width="22" height="22"></iconify-icon>',
    'Essen & Trinken': '<iconify-icon icon="lucide:utensils" width="22" height="22"></iconify-icon>',
    'Technik & Medien': '<iconify-icon icon="lucide:cpu" width="22" height="22"></iconify-icon>',
    'Wohnen & Haushalt': '<iconify-icon icon="lucide:home" width="22" height="22"></iconify-icon>',
    'Einkaufen & Geld': '<iconify-icon icon="lucide:shopping-bag" width="22" height="22"></iconify-icon>',
    'Kunst & Unterhaltung': '<iconify-icon icon="lucide:music" width="22" height="22"></iconify-icon>',
    'Zeit & Alltag': '<iconify-icon icon="lucide:clock" width="22" height="22"></iconify-icon>',
    'Wirtschaft & Finanzen': '<iconify-icon icon="lucide:trending-up" width="22" height="22"></iconify-icon>',
    'Freizeit & Sport': '<iconify-icon icon="lucide:zap" width="22" height="22"></iconify-icon>',
    'Philosophie & Erkenntnistheorie': '<iconify-icon icon="lucide:microscope" width="22" height="22"></iconify-icon>',
    'Wissenschaft & Medizin': '<iconify-icon icon="lucide:microscope" width="22" height="22"></iconify-icon>',
    'Aemter & Buerokratie': '<iconify-icon icon="lucide:landmark" width="22" height="22"></iconify-icon>',
    'Natur & Wetter': '<iconify-icon icon="lucide:sun" width="22" height="22"></iconify-icon>',
    'Familie & Menschen': '<iconify-icon icon="lucide:users" width="22" height="22"></iconify-icon>',
    'Kleidung & Aussehen': '<iconify-icon icon="lucide:shirt" width="22" height="22"></iconify-icon>',
    'Stadt & Orte': '<iconify-icon icon="lucide:compass" width="22" height="22"></iconify-icon>',
    'Sprache & Literatur': '<iconify-icon icon="lucide:book-open" width="22" height="22"></iconify-icon>',
    'Gesellschaft & Kultur': '<iconify-icon icon="lucide:users" width="22" height="22"></iconify-icon>',
    'Zahlen & Zeit': '<iconify-icon icon="lucide:clock" width="22" height="22"></iconify-icon>',
    'Feste & Traditionen': '<iconify-icon icon="lucide:gift" width="22" height="22"></iconify-icon>',
    'Sicherheit & Notfaelle': '<iconify-icon icon="lucide:activity" width="22" height="22"></iconify-icon>',
    'Wohnungssuche & Umzug': '<iconify-icon icon="lucide:package" width="22" height="22"></iconify-icon>',
    'Tiere & Pflanzen': '<iconify-icon icon="lucide:paw-print" width="22" height="22"></iconify-icon>',
    'Beziehungsleben & Liebe': '<iconify-icon icon="lucide:heart" width="22" height="22"></iconify-icon>',
    'Farben': '<iconify-icon icon="lucide:palette" width="22" height="22"></iconify-icon>',
    'Moebel': '<iconify-icon icon="lucide:home" width="22" height="22"></iconify-icon>',
    'Zahlen & Mengen': '<iconify-icon icon="lucide:hash" width="22" height="22"></iconify-icon>',
    'Farben & Formen': '<iconify-icon icon="lucide:palette" width="22" height="22"></iconify-icon>',
    'Feste & Feiern': '<iconify-icon icon="lucide:gift" width="22" height="22"></iconify-icon>',
    'Familie & Beziehungen': '<iconify-icon icon="lucide:users" width="22" height="22"></iconify-icon>',
    // Aliases
    'Lernen & Bildung': '<iconify-icon icon="lucide:graduation-cap" width="22" height="22"></iconify-icon>',
    'Beruf & Arbeit': '<iconify-icon icon="lucide:briefcase" width="22" height="22"></iconify-icon>',
    'Natur, Wetter & Umwelt': '<iconify-icon icon="lucide:sun" width="22" height="22"></iconify-icon>',
    'Freizeit, Sport & Hobbys': '<iconify-icon icon="lucide:zap" width="22" height="22"></iconify-icon>',
    'Aemter, Behoerden & Recht': '<iconify-icon icon="lucide:landmark" width="22" height="22"></iconify-icon>',
    'Medien & Kommunikation': '<iconify-icon icon="lucide:smartphone" width="22" height="22"></iconify-icon>',
    'Gefuehle & Beziehungen': '<iconify-icon icon="lucide:heart" width="22" height="22"></iconify-icon>',
    'Feste, Feiern & Geschenke': '<iconify-icon icon="lucide:gift" width="22" height="22"></iconify-icon>',
    'Sonstiges': '<iconify-icon icon="lucide:folder" width="22" height="22"></iconify-icon>'
  };

  const CATEGORY_VI = {
    // 39 Active categories from words_final.json
    'Allgemein': 'Từ vựng thông dụng & Cơ bản',
    'Arbeit & Beruf': 'Nghề nghiệp & Công việc',
    'Argumentation & Analyse': 'Lập luận & Phân tích',
    'Verkehr & Reisen': 'Giao thông & Du lịch',
    'Schule & Bildung': 'Trường học & Giáo dục',
    'Koerper & Gesundheit': 'Thân thể & Sức khỏe',
    'Recht & Politik': 'Pháp luật & Chính trị',
    'Gesellschaft & Umwelt': 'Xã hội & Môi trường',
    'Gefuehle & Charakter': 'Cảm xúc & Tính cách',
    'Kommunikation & Sprache': 'Giao tiếp & Ngôn ngữ',
    'Essen & Trinken': 'Ăn uống & Thực phẩm',
    'Technik & Medien': 'Kỹ thuật & Công nghệ',
    'Wohnen & Haushalt': 'Nhà ở & Gia dụng',
    'Einkaufen & Geld': 'Mua sắm & Tiền bạc',
    'Kunst & Unterhaltung': 'Nghệ thuật & Giải trí',
    'Zeit & Alltag': 'Thời gian & Đời sống',
    'Wirtschaft & Finanzen': 'Kinh tế & Tài chính',
    'Freizeit & Sport': 'Giải trí & Thể thao',
    'Philosophie & Erkenntnistheorie': 'Triết học & Nhận thức luận',
    'Wissenschaft & Medizin': 'Khoa học & Y học',
    'Aemter & Buerokratie': 'Cơ quan & Thủ tục hành chính',
    'Natur & Wetter': 'Tự nhiên & Thời tiết',
    'Familie & Menschen': 'Gia đình & Con người',
    'Kleidung & Aussehen': 'Trang phục & Ngoại hình',
    'Stadt & Orte': 'Thành phố & Địa điểm',
    'Sprache & Literatur': 'Ngôn ngữ & Văn học',
    'Gesellschaft & Kultur': 'Xã hội & Văn hóa',
    'Zahlen & Zeit': 'Con số & Thời gian',
    'Feste & Traditionen': 'Lễ hội & Truyền thống',
    'Sicherheit & Notfaelle': 'An ninh & Tình huống khẩn cấp',
    'Wohnungssuche & Umzug': 'Thuê nhà & Chuyển nhà',
    'Tiere & Pflanzen': 'Động vật & Cây cỏ',
    'Beziehungsleben & Liebe': 'Tình yêu & Hôn nhân',
    'Farben': 'Màu sắc',
    'Moebel': 'Đồ đạc & Nội thất',
    'Zahlen & Mengen': 'Con số & Số lượng',
    'Farben & Formen': 'Màu sắc & Hình khối',
    'Feste & Feiern': 'Lễ hội & Tiệc tùng',
    'Familie & Beziehungen': 'Gia đình & Quan hệ',
    // Aliases
    'Lernen & Bildung': 'Học tập & Giáo dục',
    'Beruf & Arbeit': 'Nghề nghiệp & Việc làm',
    'Natur, Wetter & Umwelt': 'Tự nhiên & Thời tiết',
    'Freizeit, Sport & Hobbys': 'Giải trí & Thể thao',
    'Aemter, Behoerden & Recht': 'Cơ quan & Pháp luật',
    'Medien & Kommunikation': 'Truyền thông & Liên lạc',
    'Gefuehle & Beziehungen': 'Cảm xúc & Mối quan hệ',
    'Feste, Feiern & Geschenke': 'Lễ hội & Quà tặng',
    'Sonstiges': 'Chủ đề khác'
  };

  // Initialization
  async function init() {
    cacheDom();
    bindEvents();
    checkTtsServer();
    initServiceWorker();
    initPwaInstall();
    await loadInitialData();
    checkForAppUpdates();
  }

  function cacheDom() {
    el.serverStatusPill = document.getElementById('server-status-pill');
    el.levelChips = document.querySelectorAll('.level-chip');
    el.navBtns = document.querySelectorAll('.nav-item-btn');
    el.tabPanes = document.querySelectorAll('.tab-pane');
    
    // Dict tab
    el.searchInput = document.getElementById('search-input');
    el.searchClearBtn = document.getElementById('search-clear-btn');
    el.filterPills = document.querySelectorAll('.filter-pill');
    el.wordListContainer = document.getElementById('word-list-container');
    el.dictCountPill = document.getElementById('dict-count-pill');
    el.loadMoreContainer = document.getElementById('load-more-container');
    el.loadMoreBtn = document.getElementById('load-more-btn');
    
    // Themes tab
    el.themesContainer = document.getElementById('themes-container');
    el.themeWordsContainer = document.getElementById('theme-words-container');
    el.themeBackBtn = document.getElementById('theme-back-btn');
    el.themeTitle = document.getElementById('theme-title');
    
    // Sentences tab
    el.letterScroller = document.getElementById('letter-scroller');
    el.sentencesList = document.getElementById('sentences-list');
    el.sentenceSearch = document.getElementById('sentence-search');
    
    // Grammar tab
    el.grammarList = document.getElementById('grammar-list');
    
    // Practice tab - 4 Modes & Scenes
    el.modeFlashcardBtn = document.getElementById('mode-flashcard-btn');
    el.modeMatchBtn = document.getElementById('mode-match-btn');
    el.modeQuizDeViBtn = document.getElementById('mode-quiz-de-vi-btn');
    el.modeQuizViDeBtn = document.getElementById('mode-quiz-vi-de-btn');

    el.flashcardScene = document.getElementById('flashcard-scene');
    el.matchScene = document.getElementById('match-scene');
    el.quizScene = document.getElementById('quiz-scene');
    el.quizViDeScene = document.getElementById('quiz-vi-de-scene');

    // 1. Flashcard elements
    el.flashcardInner = document.getElementById('flashcard-inner');
    el.cardDe = document.getElementById('card-de');
    el.cardArt = document.getElementById('card-art');
    el.cardVi = document.getElementById('card-vi');
    el.cardExDe = document.getElementById('card-ex-de');
    el.cardExVi = document.getElementById('card-ex-vi');
    el.cardLevel = document.getElementById('card-level');
    el.cardSpeakerBtn = document.getElementById('card-speaker-btn');
    el.btnFail = document.getElementById('btn-card-fail');
    el.btnPass = document.getElementById('btn-card-pass');
    el.cardCounter = document.getElementById('card-counter');

    // 2. Match Game elements
    el.matchCounterPill = document.getElementById('match-counter-pill');
    el.matchTriesPill = document.getElementById('match-tries-pill');
    el.btnMatchRestart = document.getElementById('btn-match-restart');
    el.matchGrid = document.getElementById('match-grid');
    el.matchWinBox = document.getElementById('match-win-box');

    // 3. Quiz DE -> VI elements
    el.quizQuestionText = document.getElementById('quiz-question-text');
    el.quizOptionsContainer = document.getElementById('quiz-options-container');
    el.quizProgress = document.getElementById('quiz-progress');
    el.quizSpeakerBtn = document.getElementById('quiz-speaker-btn');

    // 4. Quiz VI -> DE elements
    el.quizViDeProgress = document.getElementById('quiz-vi-de-progress');
    el.quizViDeMeaning = document.getElementById('quiz-vi-de-meaning');
    el.quizViDeHint = document.getElementById('quiz-vi-de-hint');
    el.quizViDeOptionsContainer = document.getElementById('quiz-vi-de-options-container');
    
    // Conjugation Drawer
    el.drawerBackdrop = document.getElementById('drawer-backdrop');
    el.drawerSheet = document.getElementById('drawer-sheet');
    el.drawerVerbTitle = document.getElementById('drawer-verb-title');
    el.drawerVerbVi = document.getElementById('drawer-verb-vi');
    el.drawerBody = document.getElementById('drawer-body');
    el.drawerCloseBtn = document.getElementById('drawer-close-btn');

    // Toast
    el.toast = document.getElementById('glass-toast');
  }

  function bindEvents() {
    // Navigation tabs
    el.navBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        switchTab(tab);
      });
    });

    // Level chips
    el.levelChips.forEach(chip => {
      chip.addEventListener('click', () => {
        el.levelChips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        state.currentLevel = chip.dataset.level;
        onLevelChanged();
      });
    });

    // Search input
    let searchDebounceTimer = null;
    el.searchInput.addEventListener('input', (e) => {
      const val = e.target.value.trim();
      state.searchQuery = val;
      el.searchClearBtn.classList.toggle('visible', val.length > 0);
      
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        state.page = 1;
        applyFilters();
      }, 150);
    });

    el.searchClearBtn.addEventListener('click', () => {
      el.searchInput.value = '';
      state.searchQuery = '';
      el.searchClearBtn.classList.remove('visible');
      state.page = 1;
      applyFilters();
    });

    // POS Filter pills
    el.filterPills.forEach(pill => {
      pill.addEventListener('click', () => {
        el.filterPills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        state.currentFilterPos = pill.dataset.pos;
        state.page = 1;
        applyFilters();
      });
    });

    // Load More button
    if (el.loadMoreBtn) {
      el.loadMoreBtn.addEventListener('click', () => {
        state.page++;
        renderWordCards(false);
      });
    }

    // Infinite scroll load more on window scroll
    window.addEventListener('scroll', () => {
      if (state.currentTab !== 'dict' && !state.selectedCategory) return;
      if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 500) {
        if (state.page * state.pageSize < state.wordsFiltered.length) {
          state.page++;
          renderWordCards(false);
        }
      }
    }, { passive: true });

    // Drawer close
    el.drawerBackdrop.addEventListener('click', closeDrawer);
    el.drawerCloseBtn.addEventListener('click', closeDrawer);

    // Theme back button
    el.themeBackBtn.addEventListener('click', () => {
      state.selectedCategory = null;
      el.themeWordsContainer.style.display = 'none';
      el.themesContainer.style.display = 'grid';
    });

    // Flashcard events
    el.flashcardInner.addEventListener('click', () => {
      state.flashcardFlipped = !state.flashcardFlipped;
      el.flashcardInner.classList.toggle('flipped', state.flashcardFlipped);
    });

    el.cardSpeakerBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const current = state.flashcardList[state.flashcardIndex];
      if (current) playTTS(current.de);
    });

    el.btnPass.addEventListener('click', () => nextFlashcard(true));
    el.btnFail.addEventListener('click', () => nextFlashcard(false));

    // Practice Mode Switcher (4 Modes)
    if (el.modeFlashcardBtn) {
      el.modeFlashcardBtn.addEventListener('click', () => setPracticeMode('flashcard'));
    }
    if (el.modeMatchBtn) {
      el.modeMatchBtn.addEventListener('click', () => setPracticeMode('match'));
    }
    if (el.modeQuizDeViBtn) {
      el.modeQuizDeViBtn.addEventListener('click', () => setPracticeMode('quiz-de-vi'));
    }
    if (el.modeQuizViDeBtn) {
      el.modeQuizViDeBtn.addEventListener('click', () => setPracticeMode('quiz-vi-de'));
    }

    // Match restart button
    if (el.btnMatchRestart) {
      el.btnMatchRestart.addEventListener('click', () => initMatchGame());
    }

    // Quiz speaker button
    if (el.quizSpeakerBtn) {
      el.quizSpeakerBtn.addEventListener('click', () => {
        const q = state.quizQuestions[state.quizIndex];
        if (q && q.word) playTTS(q.word.de, el.quizSpeakerBtn);
      });
    }

    // Server status pill click to test audio or change IP
    el.serverStatusPill.addEventListener('click', async () => {
      showToast('Đang kiểm tra kết nối Thorsten TTS...');
      await checkTtsServer();
      if (state.isTtsOnline) {
        showToast('Đã kết nối máy chủ Thorsten TTS!');
        playTTS('Hallo! Willkommen bei KAII.');
      } else {
        const newIp = prompt('Nhập địa chỉ máy tính chạy server (ví dụ: http://192.168.1.5:8080):', SERVER_BASE_URL);
        if (newIp && newIp.trim()) {
          SERVER_BASE_URL = newIp.trim().replace(/\/+$/, '');
          localStorage.setItem('kaii_server_ip', SERVER_BASE_URL);
          showToast('Đã lưu địa chỉ máy chủ: ' + SERVER_BASE_URL);
          checkTtsServer();
        } else {
          showToast('Đang dùng giọng máy offline.');
          playTTS('Hallo! Willkommen bei KAII.');
        }
      }
    });

    // KAII Cyber Avatar interactive tap
    const kaiiAvatarBtn = document.getElementById('btn-kaii-avatar');
    if (kaiiAvatarBtn) {
      kaiiAvatarBtn.addEventListener('click', () => {
        kaiiAvatarBtn.classList.add('avatar-tapped');
        setTimeout(() => kaiiAvatarBtn.classList.remove('avatar-tapped'), 600);
        showToast('⚡ KAII Cyber Edition — Hết token thì cứ gọi là quẩy tiếp!');
        playTTS('Hallo! Ich bin KAII. Willkommen!');
      });
    }

    // Sentence search
    let sentenceDebounce = null;
    el.sentenceSearch.addEventListener('input', (e) => {
      clearTimeout(sentenceDebounce);
      sentenceDebounce = setTimeout(() => {
        renderSentences();
      }, 150);
    });
  }

  // ==========================================================================
  // Data Loading
  // ==========================================================================
  async function loadInitialData() {
    try {
      showToast('Đang tải kho từ vựng tiếng Đức...');
      
      const [wordsRes, conjRes, sentRes, gramRes] = await Promise.all([
        fetch('/words_final.json').then(r => r.json()),
        fetch('/conjugations.json').then(r => r.json()).catch(() => ({})),
        fetch('/sentences_final.json').then(r => r.json()).catch(() => ({})),
        fetch('/grammar_summary.json').then(r => r.json()).catch(() => ({}))
      ]);

      state.words = wordsRes || [];
      state.conjugations = conjRes || {};
      state.sentences = sentRes || {};
      state.grammar = gramRes || {};

      showToast(`Đã tải sẵn sàng ${state.words.length.toLocaleString()} từ Đức - Việt!`);
      applyFilters();
      renderThemes();
      renderLetterScroller();
      renderSentences();
      renderGrammar();
      initFlashcards();
    } catch (err) {
      console.error('Data load error:', err);
      showToast('Không thể kết nối tải dữ liệu từ máy chủ local.');
    }
  }

  // ==========================================================================
  // Navigation & Level Switcher
  // ==========================================================================
  function switchTab(tabId) {
    state.currentTab = tabId;
    el.navBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tab === tabId);
    });

    el.tabPanes.forEach(pane => {
      pane.classList.toggle('active', pane.id === `tab-${tabId}`);
    });

    window.scrollTo({ top: 0, behavior: 'smooth' });

    if (tabId === 'practice') {
      if (state.practiceMode === 'flashcard') initFlashcards();
      else if (state.practiceMode === 'match') initMatchGame();
      else if (state.practiceMode === 'quiz-de-vi') initQuizDeVi();
      else if (state.practiceMode === 'quiz-vi-de') initQuizViDe();
    }
  }

  function onLevelChanged() {
    if (state.currentTab === 'dict') {
      state.page = 1;
      applyFilters();
    } else if (state.currentTab === 'themes') {
      renderThemes();
    } else if (state.currentTab === 'sentences') {
      renderSentences();
    } else if (state.currentTab === 'grammar') {
      renderGrammar();
    } else if (state.currentTab === 'practice') {
      if (state.practiceMode === 'flashcard') initFlashcards();
      else if (state.practiceMode === 'match') initMatchGame();
      else if (state.practiceMode === 'quiz-de-vi') initQuizDeVi();
      else if (state.practiceMode === 'quiz-vi-de') initQuizViDe();
    }
  }

  // ==========================================================================
  // Tab 1: Dictionary & Word Cards
  // ==========================================================================
  function applyFilters() {
    const q = state.searchQuery.toLowerCase().trim();
    const lvl = state.currentLevel;
    const pos = state.currentFilterPos;

    state.wordsFiltered = state.words.filter(w => {
      // Level filter
      if (lvl !== 'ALL' && w.level !== lvl) return false;

      // POS filter
      if (pos !== 'ALL') {
        const art = (w.article || '').toLowerCase();
        const de = (w.de || '').toLowerCase();
        if (pos === 'nomen') {
          if (!['m.', 'f.', 'n.', 'pl.'].includes(art) && !de.startsWith('der ') && !de.startsWith('die ') && !de.startsWith('das ')) return false;
        } else if (pos === 'verben') {
          if (['m.', 'f.', 'n.', 'pl.'].includes(art)) return false;
          if (w.pos && w.pos !== 'verb') return false;
        } else if (pos === 'adjektive') {
          if (w.pos && w.pos !== 'adjective') return false;
        }
      }

      // Search query
      if (q) {
        const de = (w.de || '').toLowerCase();
        const vi = (w.vi || '').toLowerCase();
        const ex = (w.example || '').toLowerCase();
        const exVi = (w.example_vi || '').toLowerCase();
        if (!de.includes(q) && !vi.includes(q) && !ex.includes(q) && !exVi.includes(q)) return false;
      }

      return true;
    });

    el.dictCountPill.textContent = `${state.wordsFiltered.length.toLocaleString()} từ`;
    renderWordCards(true);
  }

  function renderWordCards(reset = true) {
    if (reset) {
      el.wordListContainer.innerHTML = '';
      state.page = 1;
    }

    const start = (state.page - 1) * state.pageSize;
    const end = state.page * state.pageSize;
    const chunk = state.wordsFiltered.slice(start, end);

    if (state.wordsFiltered.length === 0) {
      el.wordListContainer.innerHTML = `
        <div class="glass-card" style="text-align:center;padding:40px 20px;">
          <div style="margin-bottom:10px;color:var(--text-muted);">
            <iconify-icon icon="lucide:search" width="40" height="40"></iconify-icon>
          </div>
          <div style="font-weight:700;font-size:1.1rem;margin-bottom:6px;">Không tìm thấy từ nào</div>
          <div style="font-size:0.85rem;color:var(--text-muted);">Hãy thử nhập từ khóa khác hoặc bỏ chọn bộ lọc cấp độ.</div>
        </div>
      `;
      el.loadMoreContainer.style.display = 'none';
      return;
    }

    const fragment = document.createDocumentFragment();
    chunk.forEach(w => {
      const card = createWordCardElement(w);
      fragment.appendChild(card);
    });

    el.wordListContainer.appendChild(fragment);

    // Toggle load more button
    el.loadMoreContainer.style.display = (end < state.wordsFiltered.length) ? 'block' : 'none';
  }

  function createWordCardElement(w) {
    const card = document.createElement('div');
    card.className = 'glass-card word-card';

    // Parse German word and article badge
    const deText = w.de || '';
    let artClass = '';
    let artLabel = '';
    let displayWord = deText;

    if (w.article === 'm.' || deText.startsWith('der ')) {
      artClass = 'art-der';
      artLabel = 'der';
      if (deText.startsWith('der ')) displayWord = deText.substring(4);
    } else if (w.article === 'f.' || deText.startsWith('die ')) {
      artClass = 'art-die';
      artLabel = 'die';
      if (deText.startsWith('die ')) displayWord = deText.substring(4);
    } else if (w.article === 'n.' || deText.startsWith('das ')) {
      artClass = 'art-das';
      artLabel = 'das';
      if (deText.startsWith('das ')) displayWord = deText.substring(4);
    } else if (w.article === 'pl.') {
      artClass = 'art-pl';
      artLabel = 'pl.';
    }

    const artBadgeHtml = artLabel ? `<span class="art-badge ${artClass}">${artLabel}</span>` : '';
    const levelHtml = w.level ? `<span class="badge-level">${w.level}</span>` : '';
    
    // Check if verb has conjugation
    const cleanVerbKey = deText.replace(/^sich\s+/, '').trim().toLowerCase();
    const hasConjugation = state.conjugations[cleanVerbKey] || state.conjugations[deText.toLowerCase()];

    // Has person drills
    const hasDrills = Array.isArray(w.person_sentences) && w.person_sentences.length > 0;

    card.innerHTML = `
      <div class="word-card-top">
        <div class="word-main-info">
          <div class="word-german">
            ${artBadgeHtml}
            <span>${escapeHtml(displayWord)}</span>
            ${levelHtml}
          </div>
          <div class="word-meaning-vi">${escapeHtml(w.vi || '—')}</div>
        </div>
        <button class="btn-speaker" aria-label="Phát âm">
          <iconify-icon icon="lucide:volume-2" width="16" height="16"></iconify-icon>
        </button>
      </div>

      ${w.example ? `
        <div class="word-example-box">
          <div class="ex-de">${escapeHtml(w.example)}</div>
          <div class="ex-vi">${escapeHtml(w.example_vi || '')}</div>
        </div>
      ` : ''}

      <div class="word-actions">
        ${hasConjugation ? `<button class="btn-glass-action btn-conj"><iconify-icon icon="lucide:book-open" width="13" height="13"></iconify-icon> Chia động từ</button>` : ''}
        ${hasDrills ? `<button class="btn-glass-action btn-drill"><iconify-icon icon="lucide:users" width="13" height="13"></iconify-icon> Theo ngôi (${w.person_sentences.length})</button>` : ''}
      </div>

      ${hasDrills ? `
        <div class="person-drills-list">
          ${w.person_sentences.map(p => `
            <div class="drill-row">
              <span class="ex-de" style="font-weight:600;">${escapeHtml(p[0])}</span>
            </div>
          `).join('')}
        </div>
      ` : ''}
    `;

    // Audio button click
    const speakerBtn = card.querySelector('.btn-speaker');
    speakerBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      playTTS(w.de, speakerBtn);
    });

    // Example sentence tap to speak
    const exDe = card.querySelector('.ex-de');
    if (exDe) {
      exDe.addEventListener('click', (e) => {
        e.stopPropagation();
        playTTS(w.example);
      });
    }

    // Conjugation button click
    const conjBtn = card.querySelector('.btn-conj');
    if (conjBtn) {
      conjBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        openDrawer(cleanVerbKey, w.vi);
      });
    }

    // Person drill button toggle
    const drillBtn = card.querySelector('.btn-drill');
    const drillList = card.querySelector('.person-drills-list');
    if (drillBtn && drillList) {
      drillBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        drillList.classList.toggle('open');
      });
    }

    return card;
  }

  // ==========================================================================
  // Tab 2: Wortschatz by Themes
  // ==========================================================================
  function renderThemes() {
    el.themesContainer.innerHTML = '';
    const lvl = state.currentLevel;

    // Count categories
    const counts = {};
    state.words.forEach(w => {
      if (lvl !== 'ALL' && w.level !== lvl) return;
      const cat = w.category || 'Sonstiges';
      counts[cat] = (counts[cat] || 0) + 1;
    });

    const categories = Object.keys(counts).sort((a, b) => counts[b] - counts[a]);

    categories.forEach(cat => {
      const card = document.createElement('div');
      card.className = 'theme-glass-card';
      const icon = CATEGORY_ICONS[cat] || '<iconify-icon icon="lucide:folder" width="22" height="22"></iconify-icon>';
      const nameVi = CATEGORY_VI[cat] || cat;

      card.innerHTML = `
        <div class="theme-icon">${icon}</div>
        <div>
          <div class="theme-name-de">${escapeHtml(cat)}</div>
          <div class="theme-name-vi">${escapeHtml(nameVi)}</div>
        </div>
        <div class="theme-count">${counts[cat]} từ</div>
      `;

      card.addEventListener('click', () => {
        openThemeCategory(cat, nameVi);
      });

      el.themesContainer.appendChild(card);
    });
  }

  function openThemeCategory(cat, nameVi) {
    state.selectedCategory = cat;
    el.themesContainer.style.display = 'none';
    el.themeWordsContainer.style.display = 'block';
    el.themeTitle.textContent = `${cat} (${nameVi})`;

    // Filter words belonging to this theme
    const lvl = state.currentLevel;
    const catWords = state.words.filter(w => {
      if (lvl !== 'ALL' && w.level !== lvl) return false;
      return (w.category || 'Sonstiges') === cat;
    });

    const list = document.getElementById('theme-word-list');
    list.innerHTML = '';
    const fragment = document.createDocumentFragment();
    catWords.forEach(w => {
      fragment.appendChild(createWordCardElement(w));
    });
    list.appendChild(fragment);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  // ==========================================================================
  // Tab 3: Sätze A-Z
  // ==========================================================================
  function renderLetterScroller() {
    el.letterScroller.innerHTML = '';
    const letters = ['ALL', ...'ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ'.split('')];
    
    letters.forEach(char => {
      const chip = document.createElement('div');
      chip.className = `letter-chip ${char === state.selectedLetter ? 'active' : ''}`;
      chip.textContent = char;
      chip.addEventListener('click', () => {
        el.letterScroller.querySelectorAll('.letter-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        state.selectedLetter = char;
        renderSentences();
      });
      el.letterScroller.appendChild(chip);
    });
  }

  function renderSentences() {
    el.sentencesList.innerHTML = '';
    const lvl = state.currentLevel;
    const search = el.sentenceSearch.value.toLowerCase().trim();
    const letter = state.selectedLetter;

    let pool = [];
    if (lvl === 'ALL') {
      Object.keys(state.sentences).forEach(k => {
        pool = pool.concat(state.sentences[k] || []);
      });
    } else {
      pool = state.sentences[lvl] || [];
    }

    const filtered = pool.filter(s => {
      const de = (s.de || '').trim();
      const vi = (s.vi || '').trim();

      if (letter !== 'ALL') {
        const first = de.charAt(0).toUpperCase();
        if (first !== letter) return false;
      }

      if (search) {
        if (!de.toLowerCase().includes(search) && !vi.toLowerCase().includes(search)) return false;
      }

      return true;
    });

    if (filtered.length === 0) {
      el.sentencesList.innerHTML = `
        <div class="glass-card" style="text-align:center;padding:30px 16px;">
          <div style="margin-bottom:8px;color:var(--text-muted);">
            <iconify-icon icon="lucide:message-square" width="36" height="36"></iconify-icon>
          </div>
          <div>Không tìm thấy mẫu câu phù hợp.</div>
        </div>
      `;
      return;
    }

    const fragment = document.createDocumentFragment();
    filtered.slice(0, 100).forEach(s => {
      const card = document.createElement('div');
      card.className = 'glass-card sentence-card';
      card.innerHTML = `
        <div class="sentence-card-header">
          <div class="sentence-de">${escapeHtml(s.de)}</div>
          <button class="btn-speaker" aria-label="Phát âm">
            <iconify-icon icon="lucide:volume-2" width="16" height="16"></iconify-icon>
          </button>
        </div>
        <div class="sentence-vi">${escapeHtml(s.vi)}</div>
      `;

      const btn = card.querySelector('.btn-speaker');
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        playTTS(s.de, btn);
      });

      fragment.appendChild(card);
    });

    el.sentencesList.appendChild(fragment);
  }

  // ==========================================================================
  // Tab 4: Grammatik Summaries
  // ==========================================================================
  function renderGrammar() {
    el.grammarList.innerHTML = '';
    const lvl = state.currentLevel === 'ALL' ? 'A1' : state.currentLevel;
    const topics = state.grammar[lvl] || [];

    if (topics.length === 0) {
      el.grammarList.innerHTML = `
        <div class="glass-card" style="text-align:center;padding:30px 16px;">
          <div>Chưa có dữ liệu tóm tắt cho cấp độ này.</div>
        </div>
      `;
      return;
    }

    topics.forEach((t, index) => {
      const item = document.createElement('div');
      item.className = 'grammar-accordion';
      if (index === 0) item.classList.add('open');

      // Auto-wrap tables in table-scroll-wrapper with swipe hint so tables never get cut off on mobile
      let formattedHtml = t.html || '';
      formattedHtml = formattedHtml.replace(/<table\b([^>]*)>([\s\S]*?)<\/table>/gi, (match) => {
        return `
          <div class="table-scroll-wrapper">
            <div class="table-scroll-hint">
              <iconify-icon icon="lucide:arrow-right" width="12" height="12"></iconify-icon> Vuốt ngang để xem trọn vẹn bảng
            </div>
            ${match}
          </div>
        `;
      });

      item.innerHTML = `
        <div class="grammar-header">
          <h3>${escapeHtml(t.title)}</h3>
          <span class="grammar-arrow"><iconify-icon icon="lucide:chevron-down" width="14" height="14"></iconify-icon></span>
        </div>
        <div class="grammar-content">
          ${formattedHtml}
        </div>
      `;

      item.querySelector('.grammar-header').addEventListener('click', () => {
        item.classList.toggle('open');
      });

      el.grammarList.appendChild(item);
    });
  }

  // ==========================================================================
  // Tab 5: Practice (Flashcards, Match Game, Quiz DE->VI, Quiz VI->DE)
  // ==========================================================================
  function setPracticeMode(mode) {
    state.practiceMode = mode;

    el.modeFlashcardBtn.classList.toggle('active', mode === 'flashcard');
    el.modeMatchBtn.classList.toggle('active', mode === 'match');
    el.modeQuizDeViBtn.classList.toggle('active', mode === 'quiz-de-vi');
    el.modeQuizViDeBtn.classList.toggle('active', mode === 'quiz-vi-de');

    el.flashcardScene.style.display = (mode === 'flashcard') ? 'block' : 'none';
    el.matchScene.style.display = (mode === 'match') ? 'block' : 'none';
    el.quizScene.style.display = (mode === 'quiz-de-vi') ? 'block' : 'none';
    el.quizViDeScene.style.display = (mode === 'quiz-vi-de') ? 'block' : 'none';

    if (mode === 'flashcard') initFlashcards();
    else if (mode === 'match') initMatchGame();
    else if (mode === 'quiz-de-vi') initQuizDeVi();
    else if (mode === 'quiz-vi-de') initQuizViDe();
  }

  // 1. Flashcard 3D Logic
  function initFlashcards() {
    const lvl = state.currentLevel;
    const pool = state.words.filter(w => (lvl === 'ALL' || w.level === lvl) && w.vi);
    
    // Shuffle
    state.flashcardList = pool.sort(() => 0.5 - Math.random()).slice(0, 50);
    state.flashcardIndex = 0;
    state.flashcardScore = { known: 0, total: state.flashcardList.length };
    
    renderCurrentFlashcard();
  }

  function renderCurrentFlashcard() {
    if (state.flashcardList.length === 0) return;
    const w = state.flashcardList[state.flashcardIndex];
    if (!w) return;

    state.flashcardFlipped = false;
    el.flashcardInner.classList.remove('flipped');

    // Parse German word & article
    const deText = w.de || '';
    let artLabel = '';
    let artClass = '';
    let displayWord = deText;

    if (w.article === 'm.' || deText.startsWith('der ')) {
      artClass = 'art-der'; artLabel = 'der';
      if (deText.startsWith('der ')) displayWord = deText.substring(4);
    } else if (w.article === 'f.' || deText.startsWith('die ')) {
      artClass = 'art-die'; artLabel = 'die';
      if (deText.startsWith('die ')) displayWord = deText.substring(4);
    } else if (w.article === 'n.' || deText.startsWith('das ')) {
      artClass = 'art-das'; artLabel = 'das';
      if (deText.startsWith('das ')) displayWord = deText.substring(4);
    }

    el.cardArt.className = `art-badge ${artClass}`;
    el.cardArt.textContent = artLabel;
    el.cardArt.style.display = artLabel ? 'inline-block' : 'none';

    el.cardDe.textContent = displayWord;
    el.cardLevel.textContent = w.level || 'A1';
    el.cardVi.textContent = w.vi || '';
    el.cardExDe.textContent = w.example || '';
    el.cardExVi.textContent = w.example_vi || '';

    el.cardCounter.textContent = `Thẻ ${state.flashcardIndex + 1} / ${state.flashcardList.length} (Đã nhớ: ${state.flashcardScore.known})`;
  }

  function nextFlashcard(known) {
    if (known) state.flashcardScore.known++;
    state.flashcardIndex++;

    if (state.flashcardIndex >= state.flashcardList.length) {
      showToast(`Hoàn thành! Đã nhớ ${state.flashcardScore.known} / ${state.flashcardList.length} từ!`);
      initFlashcards();
      return;
    }

    renderCurrentFlashcard();
  }

  // 2. Match Game (Game Nối từ Đức - Việt)
  function initMatchGame() {
    const lvl = state.currentLevel;
    const pool = state.words.filter(w => (lvl === 'ALL' || w.level === lvl) && w.vi && w.de);
    if (pool.length < 6) {
      showToast('Cần ít nhất 6 từ để chơi nối từ!');
      return;
    }

    state.matchSelectedTile = null;
    state.matchPairsCount = 6;
    state.matchPairsFound = 0;
    state.matchTries = 0;
    state.matchLocked = false;

    if (el.matchCounterPill) el.matchCounterPill.textContent = 'Cặp: 0 / 6';
    if (el.matchTriesPill) el.matchTriesPill.textContent = 'Lần thử: 0';
    if (el.matchWinBox) {
      el.matchWinBox.style.display = 'none';
      el.matchWinBox.innerHTML = '';
    }

    // Pick 6 random words
    const chosenWords = [...pool].sort(() => 0.5 - Math.random()).slice(0, 6);

    // Create 12 tiles (6 DE, 6 VI)
    const tiles = [];
    chosenWords.forEach((w, idx) => {
      tiles.push({
        pairId: idx,
        type: 'de',
        text: w.de,
        word: w
      });
      tiles.push({
        pairId: idx,
        type: 'vi',
        text: w.vi,
        word: w
      });
    });

    // Shuffle tiles
    state.matchTiles = tiles.sort(() => 0.5 - Math.random());

    // Render in grid
    el.matchGrid.innerHTML = '';
    state.matchTiles.forEach(item => {
      const tile = document.createElement('div');
      tile.className = 'match-tile';
      tile.textContent = item.text;
      tile.dataset.pairId = item.pairId;
      tile.dataset.type = item.type;

      tile.addEventListener('click', () => handleMatchTileClick(tile, item));
      el.matchGrid.appendChild(tile);
    });
  }

  function handleMatchTileClick(tileEl, item) {
    if (state.matchLocked) return;
    if (tileEl.classList.contains('matched')) return;

    // Pronounce if German tile tapped
    if (item.type === 'de') {
      playTTS(item.word.de);
    }

    // Case 1: No tile selected yet
    if (!state.matchSelectedTile) {
      tileEl.classList.add('selected');
      state.matchSelectedTile = { el: tileEl, item: item };
      return;
    }

    const prevEl = state.matchSelectedTile.el;
    const prevItem = state.matchSelectedTile.item;

    // Case 2: Clicked on same tile -> unselect
    if (prevEl === tileEl) {
      tileEl.classList.remove('selected');
      state.matchSelectedTile = null;
      return;
    }

    // Case 3: Clicked another tile of SAME language -> switch selection
    if (prevItem.type === item.type) {
      prevEl.classList.remove('selected');
      tileEl.classList.add('selected');
      state.matchSelectedTile = { el: tileEl, item: item };
      return;
    }

    // Case 4: Clicked opposite language tile -> attempt match!
    state.matchTries++;
    if (el.matchTriesPill) el.matchTriesPill.textContent = `Lần thử: ${state.matchTries}`;

    if (prevItem.pairId === item.pairId) {
      // MATCH!
      prevEl.classList.remove('selected');
      prevEl.classList.add('matched');
      tileEl.classList.add('matched');
      state.matchSelectedTile = null;
      state.matchPairsFound++;
      if (el.matchCounterPill) el.matchCounterPill.textContent = `Cặp: ${state.matchPairsFound} / ${state.matchPairsCount}`;

      // Reinforce pronunciation
      playTTS(item.word.de);

      // Check win
      if (state.matchPairsFound >= state.matchPairsCount) {
        showMatchWin();
      }
    } else {
      // MISMATCH
      state.matchLocked = true;
      prevEl.classList.add('wrong');
      tileEl.classList.add('wrong');

      setTimeout(() => {
        prevEl.classList.remove('selected', 'wrong');
        tileEl.classList.remove('selected', 'wrong');
        state.matchSelectedTile = null;
        state.matchLocked = false;
      }, 500);
    }
  }

  function showMatchWin() {
    if (!el.matchWinBox) return;
    el.matchWinBox.style.display = 'block';
    el.matchWinBox.innerHTML = `
      <div class="glass-card" style="text-align:center;padding:26px 16px;">
        <div style="font-size:2.8rem;margin-bottom:8px;color:#f59e0b;">
          <iconify-icon icon="lucide:trophy" width="48" height="48"></iconify-icon>
        </div>
        <div style="font-size:1.25rem;font-weight:800;color:#ffffff;margin-bottom:6px;">
          Xuất sắc! Đã nối đúng tất cả!
        </div>
        <div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:16px;">
          Bạn đã hoàn thành 6 cặp từ sau <strong style="color:#38bdf8;">${state.matchTries}</strong> lần thử.
        </div>
        <button id="btn-match-play-again" class="btn-card-action btn-card-pass" style="width:100%;justify-content:center;">
          <iconify-icon icon="lucide:refresh-cw" width="16" height="16"></iconify-icon> Chơi ván mới
        </button>
      </div>
    `;

    document.getElementById('btn-match-play-again').addEventListener('click', () => {
      initMatchGame();
    });
  }

  // 3. Quiz DE -> VI (Đức -> Việt)
  function initQuizDeVi() {
    const lvl = state.currentLevel;
    const pool = state.words.filter(w => (lvl === 'ALL' || w.level === lvl) && w.vi && w.de);
    if (pool.length < 4) return;

    state.quizQuestions = [];
    const shuffledPool = [...pool].sort(() => 0.5 - Math.random());

    for (let i = 0; i < 10 && i < shuffledPool.length; i++) {
      const correctWord = shuffledPool[i];
      // Pick 3 wrong options
      const wrongOptions = pool
        .filter(w => w.de !== correctWord.de)
        .sort(() => 0.5 - Math.random())
        .slice(0, 3)
        .map(w => w.vi);

      const options = [correctWord.vi, ...wrongOptions].sort(() => 0.5 - Math.random());

      state.quizQuestions.push({
        word: correctWord,
        options: options,
        correctAnswer: correctWord.vi
      });
    }

    state.quizIndex = 0;
    state.quizScore = 0;
    renderCurrentQuizDeVi();
  }

  function renderCurrentQuizDeVi() {
    if (state.quizIndex >= state.quizQuestions.length) {
      el.quizScene.innerHTML = `
        <div class="glass-card" style="text-align:center;padding:36px 20px;">
          <div style="font-size:2.8rem;margin-bottom:12px;color:#f59e0b;">
            <iconify-icon icon="lucide:trophy" width="48" height="48"></iconify-icon>
          </div>
          <div style="font-size:1.25rem;font-weight:800;margin-bottom:6px;">Kết quả Trắc nghiệm Đức → Việt</div>
          <div style="font-size:1.8rem;font-weight:900;color:#38bdf8;margin-bottom:16px;">
            ${state.quizScore} / ${state.quizQuestions.length} Điểm
          </div>
          <button id="btn-quiz-retry" class="btn-card-action btn-card-pass" style="width:100%;justify-content:center;">
            <iconify-icon icon="lucide:refresh-cw" width="16" height="16"></iconify-icon> Làm lại bài trắc nghiệm
          </button>
        </div>
      `;
      document.getElementById('btn-quiz-retry').addEventListener('click', initQuizDeVi);
      return;
    }

    const q = state.quizQuestions[state.quizIndex];
    el.quizProgress.textContent = `Câu ${state.quizIndex + 1} / ${state.quizQuestions.length} • Điểm: ${state.quizScore}`;
    el.quizQuestionText.textContent = q.word.de;

    el.quizOptionsContainer.innerHTML = '';
    q.options.forEach(opt => {
      const btn = document.createElement('button');
      btn.className = 'glass-card';
      btn.style.cssText = 'width:100%;text-align:left;padding:14px 16px;font-size:0.95rem;font-weight:600;color:#ffffff;cursor:pointer;';
      btn.textContent = opt;

      btn.addEventListener('click', () => {
        const allBtns = el.quizOptionsContainer.querySelectorAll('button');
        allBtns.forEach(b => b.disabled = true);

        if (opt === q.correctAnswer) {
          btn.style.borderColor = '#34d399';
          btn.style.background = 'rgba(16, 185, 129, 0.3)';
          state.quizScore++;
          playTTS(q.word.de);
        } else {
          btn.style.borderColor = '#f43f5e';
          btn.style.background = 'rgba(244, 63, 94, 0.3)';
          allBtns.forEach(b => {
            if (b.textContent === q.correctAnswer) {
              b.style.borderColor = '#34d399';
              b.style.background = 'rgba(16, 185, 129, 0.2)';
            }
          });
          playTTS(q.word.de);
        }

        setTimeout(() => {
          state.quizIndex++;
          renderCurrentQuizDeVi();
        }, 1100);
      });

      el.quizOptionsContainer.appendChild(btn);
    });
  }

  // 4. Quiz VI -> DE (Nghĩa tiếng Việt -> Chọn từ tiếng Đức đúng)
  function initQuizViDe() {
    const lvl = state.currentLevel;
    const pool = state.words.filter(w => (lvl === 'ALL' || w.level === lvl) && w.vi && w.de);
    if (pool.length < 4) return;

    state.quizViDeQuestions = [];
    const shuffledPool = [...pool].sort(() => 0.5 - Math.random());

    for (let i = 0; i < 10 && i < shuffledPool.length; i++) {
      const correctWord = shuffledPool[i];
      // Pick 3 wrong German options
      const wrongOptions = pool
        .filter(w => w.de !== correctWord.de)
        .sort(() => 0.5 - Math.random())
        .slice(0, 3)
        .map(w => w.de);

      const options = [correctWord.de, ...wrongOptions].sort(() => 0.5 - Math.random());

      state.quizViDeQuestions.push({
        word: correctWord,
        options: options,
        correctAnswer: correctWord.de
      });
    }

    state.quizViDeIndex = 0;
    state.quizViDeScore = 0;
    renderCurrentQuizViDe();
  }

  function renderCurrentQuizViDe() {
    if (state.quizViDeIndex >= state.quizViDeQuestions.length) {
      el.quizViDeScene.innerHTML = `
        <div class="glass-card" style="text-align:center;padding:36px 20px;">
          <div style="font-size:2.8rem;margin-bottom:12px;color:#f59e0b;">
            <iconify-icon icon="lucide:trophy" width="48" height="48"></iconify-icon>
          </div>
          <div style="font-size:1.25rem;font-weight:800;margin-bottom:6px;">Kết quả Trắc nghiệm Việt → Đức</div>
          <div style="font-size:1.8rem;font-weight:900;color:#38bdf8;margin-bottom:16px;">
            ${state.quizViDeScore} / ${state.quizViDeQuestions.length} Điểm
          </div>
          <button id="btn-quiz-vi-de-retry" class="btn-card-action btn-card-pass" style="width:100%;justify-content:center;">
            <iconify-icon icon="lucide:refresh-cw" width="16" height="16"></iconify-icon> Làm lại bài trắc nghiệm
          </button>
        </div>
      `;
      document.getElementById('btn-quiz-vi-de-retry').addEventListener('click', initQuizViDe);
      return;
    }

    const q = state.quizViDeQuestions[state.quizViDeIndex];
    el.quizViDeProgress.textContent = `Câu ${state.quizViDeIndex + 1} / ${state.quizViDeQuestions.length} • Điểm: ${state.quizViDeScore}`;
    el.quizViDeMeaning.textContent = q.word.vi;
    
    // Hint with example translation if available
    if (q.word.example_vi) {
      el.quizViDeHint.textContent = `Gợi ý ngữ cảnh: "${q.word.example_vi}"`;
      el.quizViDeHint.style.display = 'block';
    } else {
      el.quizViDeHint.style.display = 'none';
    }

    el.quizViDeOptionsContainer.innerHTML = '';
    q.options.forEach(opt => {
      const btn = document.createElement('button');
      btn.className = 'glass-card';
      btn.style.cssText = 'width:100%;text-align:left;padding:14px 16px;font-size:0.95rem;font-weight:600;color:#ffffff;cursor:pointer;';
      btn.textContent = opt;

      btn.addEventListener('click', () => {
        const allBtns = el.quizViDeOptionsContainer.querySelectorAll('button');
        allBtns.forEach(b => b.disabled = true);

        if (opt === q.correctAnswer) {
          btn.style.borderColor = '#34d399';
          btn.style.background = 'rgba(16, 185, 129, 0.3)';
          state.quizViDeScore++;
          playTTS(q.correctAnswer);
        } else {
          btn.style.borderColor = '#f43f5e';
          btn.style.background = 'rgba(244, 63, 94, 0.3)';
          allBtns.forEach(b => {
            if (b.textContent === q.correctAnswer) {
              b.style.borderColor = '#34d399';
              b.style.background = 'rgba(16, 185, 129, 0.2)';
            }
          });
          playTTS(q.correctAnswer);
        }

        setTimeout(() => {
          state.quizViDeIndex++;
          renderCurrentQuizViDe();
        }, 1200);
      });

      el.quizViDeOptionsContainer.appendChild(btn);
    });
  }

  // ==========================================================================
  // Conjugation Drawer (Bottom Sheet)
  // ==========================================================================
  function openDrawer(cleanVerb, viMeaning) {
    const conj = state.conjugations[cleanVerb];
    if (!conj) {
      showToast('Chưa có dữ liệu chia động từ cho từ này.');
      return;
    }

    el.drawerVerbTitle.textContent = conj.infinitiv || cleanVerb;
    el.drawerVerbVi.textContent = viMeaning || '';

    let html = '';
    const ind = conj.indikativ || {};

    // Helper to format tense block
    const formatTense = (title, forms) => {
      if (!Array.isArray(forms) || forms.length < 6) return '';
      const pronouns = ['ich', 'du', 'er/sie/es', 'wir', 'ihr', 'sie/Sie'];
      return `
        <div class="conj-tense-block">
          <div class="conj-tense-title">${title}</div>
          <div class="conj-grid">
            ${forms.map((f, i) => `
              <div class="conj-item" data-speak="${pronouns[i]} ${f}">
                <span class="conj-pronoun">${pronouns[i]}</span>
                <span class="conj-verb">${f}</span>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    };

    if (ind.praesens) html += formatTense('Hiện tại (Präsens)', ind.praesens);
    if (ind.praeteritum) html += formatTense('Quá khứ (Präteritum)', ind.praeteritum);
    if (ind.perfekt) html += formatTense('Hiện tại hoàn thành (Perfekt)', ind.perfekt);
    if (conj.konjunktiv2 && conj.konjunktiv2.praeteritum) {
      html += formatTense('Giả định II (Konjunktiv II)', conj.konjunktiv2.praeteritum);
    }

    if (conj.imperativ) {
      const imp = conj.imperativ;
      html += `
        <div class="conj-tense-block">
          <div class="conj-tense-title">Mệnh lệnh (Imperativ)</div>
          <div class="conj-grid">
            <div class="conj-item" data-speak="${imp.du || ''}"><span class="conj-pronoun">(du)</span><span class="conj-verb">${imp.du || '—'}</span></div>
            <div class="conj-item" data-speak="${imp.ihr || ''}"><span class="conj-pronoun">(ihr)</span><span class="conj-verb">${imp.ihr || '—'}</span></div>
            <div class="conj-item" data-speak="${imp.Sie || ''}"><span class="conj-pronoun">(Sie)</span><span class="conj-verb">${imp.Sie || '—'}</span></div>
          </div>
        </div>
      `;
    }

    el.drawerBody.innerHTML = html;

    // Attach speak event to all conj items
    el.drawerBody.querySelectorAll('.conj-item').forEach(item => {
      item.addEventListener('click', () => {
        const text = item.dataset.speak;
        if (text) playTTS(text);
      });
    });

    el.drawerBackdrop.classList.add('open');
    el.drawerSheet.classList.add('open');
  }

  function closeDrawer() {
    el.drawerBackdrop.classList.remove('open');
    el.drawerSheet.classList.remove('open');
  }

  // ==========================================================================
  // Thorsten Kokoro TTS with Native Fallback
  // ==========================================================================
  // ==========================================================================
  // Hybrid TTS (Thorsten Kokoro via LAN Server & Android Native Fallback)
  // ==========================================================================
  let SERVER_BASE_URL = localStorage.getItem('kaii_server_ip') || 'http://192.168.1.5:8080';

  async function checkTtsServer() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1200);
      const res = await fetch(`${SERVER_BASE_URL}/api/tts/health`, {
        method: 'GET',
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        state.isTtsOnline = true;
        if (el.serverStatusPill) {
          el.serverStatusPill.className = 'server-status-pill';
          el.serverStatusPill.innerHTML = '<span class="status-dot"></span> Thorsten TTS';
        }
        return;
      }
    } catch {
      // Server not reachable
    }

    state.isTtsOnline = false;
    if (el.serverStatusPill) {
      el.serverStatusPill.className = 'server-status-pill offline';
      el.serverStatusPill.innerHTML = '<span class="status-dot"></span> Giọng máy';
    }
  }

  async function playTTS(text, buttonEl) {
    if (!text) return;
    const cleanText = text.trim();

    if (buttonEl) buttonEl.classList.add('playing');

    // 1. Check in-memory audio blob cache
    if (state.audioCache.has(cleanText)) {
      const audioUrl = state.audioCache.get(cleanText);
      playAudioUrl(audioUrl, buttonEl);
      return;
    }

    // 2. If Thorsten server is reachable, generate high-quality neural voice
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(`${SERVER_BASE_URL}/api/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: cleanText, speed: 0.95 }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        const blob = await res.blob();
        const audioUrl = URL.createObjectURL(blob);
        state.audioCache.set(cleanText, audioUrl);
        playAudioUrl(audioUrl, buttonEl);
        return;
      }
    } catch (err) {
      // Failover to local speech
    }

    // 3. Fallback seamlessly to Android Native TTS (offline)
    playWebSpeech(cleanText, buttonEl);
  }

  function playAudioUrl(url, buttonEl) {
    if (state.currentAudio) {
      state.currentAudio.pause();
      state.currentAudio = null;
    }

    const audio = new Audio(url);
    state.currentAudio = audio;

    audio.onended = () => {
      if (buttonEl) buttonEl.classList.remove('playing');
      state.currentAudio = null;
    };

    audio.onerror = () => {
      if (buttonEl) buttonEl.classList.remove('playing');
      state.currentAudio = null;
    };

    audio.play().catch(e => {
      console.warn('Playback error:', e);
      if (buttonEl) buttonEl.classList.remove('playing');
    });
  }

  function playWebSpeech(text, buttonEl) {
    if (!('speechSynthesis' in window)) {
      if (buttonEl) buttonEl.classList.remove('playing');
      showToast('Thiết bị không hỗ trợ giọng đọc');
      return;
    }

    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'de-DE';
    u.rate = 0.92;

    u.onend = u.onerror = () => {
      if (buttonEl) buttonEl.classList.remove('playing');
    };

    window.speechSynthesis.speak(u);
  }

  // ==========================================================================
  // Helpers & PWA Service Worker
  // ==========================================================================
  function showToast(msg) {
    if (!el.toast) return;
    el.toast.textContent = msg;
    el.toast.classList.add('show');
    clearTimeout(el.toast._timer);
    el.toast._timer = setTimeout(() => {
      el.toast.classList.remove('show');
    }, 2800);
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function initPwaInstall() {
    let deferredInstallPrompt = null;
    const banner = document.getElementById('pwa-install-banner');
    const installBtn = document.getElementById('pwa-install-btn');
    const closeBtn = document.getElementById('pwa-close-btn');

    // Check if running already in standalone PWA / APK mode
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    if (isStandalone) {
      if (banner) banner.style.display = 'none';
      return;
    }

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredInstallPrompt = e;
      if (banner && !sessionStorage.getItem('kaii_install_dismissed')) {
        banner.style.display = 'block';
      }
    });

    if (installBtn) {
      installBtn.addEventListener('click', async () => {
        if (!deferredInstallPrompt) {
          alert('Để cài đặt KAII làm ứng dụng độc lập trên điện thoại:\n1. Nhấn nút 3 chấm ở góc trên trình duyệt\n2. Chọn "Cài đặt ứng dụng" (hoặc "Thêm vào màn hình chính")\n3. Biểu tượng KAII sẽ xuất hiện trên màn hình chính của bạn!');
          return;
        }
        deferredInstallPrompt.prompt();
        const { outcome } = await deferredInstallPrompt.userChoice;
        if (outcome === 'accepted') {
          if (banner) banner.style.display = 'none';
          showToast('🎉 Đang cài đặt KAII lên điện thoại...');
        }
        deferredInstallPrompt = null;
      });
    }

    if (closeBtn && banner) {
      closeBtn.addEventListener('click', () => {
        banner.style.display = 'none';
        sessionStorage.setItem('kaii_install_dismissed', '1');
      });
    }

    window.addEventListener('appinstalled', () => {
      if (banner) banner.style.display = 'none';
      showToast('🎉 Đã cài đặt ứng dụng KAII thành công!');
    });
  }

  function initServiceWorker() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/mobile/sw.js?v=3.6')
        .then((reg) => {
          console.log('KAII Mobile SW Registered (v3.6)');
          reg.update();
        })
        .catch(e => console.warn('SW registration:', e));
    }
  }

  // Run on DOM ready

  // ==========================================================================
  // Auto-Update Checker via GitHub Releases (ADINEBAN/kaii-deutsch)
  // ==========================================================================
  const CURRENT_APP_VERSION = '1.0.0';
  const GITHUB_REPO = 'ADINEBAN/kaii-deutsch';

  async function checkForAppUpdates() {
    try {
      // Check GitHub Releases API for the latest version tag
      const res = await fetch(`https://api.github.com/repos/${GITHUB_REPO}/releases/latest`, {
        headers: { 'Accept': 'application/vnd.github.v3+json' }
      });

      if (!res.ok) return; // No release published yet or offline

      const release = await res.json();
      const latestTag = (release.tag_name || '').replace(/^v/i, '').trim();

      if (isNewerVersion(latestTag, CURRENT_APP_VERSION)) {
        showUpdateModal(release, latestTag);
      }
    } catch (err) {
      console.log('Update check skipped (offline or not reachable):', err);
    }
  }

  function isNewerVersion(latest, current) {
    if (!latest) return false;
    const lParts = latest.split('.').map(n => parseInt(n, 10) || 0);
    const cParts = current.split('.').map(n => parseInt(n, 10) || 0);
    for (let i = 0; i < Math.max(lParts.length, cParts.length); i++) {
      const l = lParts[i] || 0;
      const c = cParts[i] || 0;
      if (l > c) return true;
      if (l < c) return false;
    }
    return false;
  }

  function showUpdateModal(release, versionStr) {
    const backdrop = document.getElementById('update-modal-backdrop');
    const titleEl = document.getElementById('update-version-title');
    const notesEl = document.getElementById('update-notes');
    const btnConfirm = document.getElementById('btn-update-now');
    const btnDismiss = document.getElementById('btn-update-dismiss');

    if (!backdrop || !titleEl || !btnConfirm) return;

    titleEl.textContent = `KAII Deutsch v${versionStr}`;
    if (release.body && release.body.trim()) {
      notesEl.textContent = release.body.trim();
    } else {
      notesEl.textContent = 'Đã có bản cập nhật mới nhất với nhiều tối ưu mượt mà và sửa lỗi.';
    }

    // Find direct APK asset if available, otherwise open the release page
    let apkUrl = release.html_url;
    if (release.assets && release.assets.length > 0) {
      const apkAsset = release.assets.find(a => a.name && a.name.endsWith('.apk'));
      if (apkAsset && apkAsset.browser_download_url) {
        apkUrl = apkAsset.browser_download_url;
      }
    }

    btnConfirm.href = apkUrl;
    btnConfirm.onclick = function(e) {
      backdrop.classList.add('hidden');
    };

    if (btnDismiss) {
      btnDismiss.onclick = function() {
        backdrop.classList.add('hidden');
      };
    }

    backdrop.classList.remove('hidden');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

