/* Shared bar of the quiz pages (quiz.html, grammar-quiz.html, placement-test.html): one row of tabs below the site header,
   so every practice mode and level test is one click away from every quiz page.
   Usage: a div with id "quiz-bar" and data-page "quiz", "grammar" or "placement", followed by a script tag loading /quiz-bar.js.
   On quiz.html the in-page modes are <button>s with the ids and data-mode that quiz.html's own script already uses
   (tab-practice, tab-hoeren, ... ; list #modeTabs); everywhere else they are links to quiz.html#<mode>. */
(function () {
  var mount = document.getElementById('quiz-bar');
  if (!mount) return;
  var page = mount.getAttribute('data-page') || '';

  var items = [
    { key: 'practice', mode: true, icon: '📚', de: 'Wortschatz', vi: 'Từ vựng' },
    { key: 'hoeren', mode: true, icon: '🎧', de: 'Hören', vi: 'Luyện nghe' },
    { key: 'lesen', mode: true, icon: '📰', de: 'Lesen', vi: 'Luyện đọc' },
    { key: 'grammar', href: '/grammar-quiz.html', icon: '🔤', de: 'Grammatik', vi: 'Ngữ pháp' },
    { key: 'placement', mode: true, icon: '🎯', de: 'Niveau: Wortschatz', vi: 'Test từ vựng' },
    { key: 'placement-grammar', href: '/placement-test.html', icon: '🎯', de: 'Niveau: Grammatik', vi: 'Test ngữ pháp' },
    { key: 'mistakes', mode: true, icon: '❌', de: 'Lỗi cần ôn', vi: 'Lỗi của tôi' },
    { key: 'bookmarks', mode: true, icon: '⭐', de: 'Đã lưu', vi: 'Xem ghi nhớ', count: true }
  ];
  var activeOnOtherPages = { grammar: 'grammar', placement: 'placement-grammar' };

  function bookmarkCount() {
    try {
      var raw = localStorage.getItem('wf_quiz_bookmarks_v1');
      return raw ? Object.keys(JSON.parse(raw)).length : 0;
    } catch (e) { return 0; }
  }

  var css = '#quiz-bar{background:rgba(11,17,32,0.95);border-bottom:1px solid rgba(255,255,255,0.08);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)}' +
    '#quiz-bar ul{display:flex;flex-wrap:wrap;justify-content:center;gap:0;list-style:none;margin:0 auto;padding:0 .5rem;max-width:1140px}' +
    '#quiz-bar li{flex:1 0 25%;min-width:0}' +
    '#quiz-bar .qb-item{display:block;width:100%;background:none;border:0;border-bottom:3px solid transparent;border-radius:0;padding:.5rem .25rem;text-align:center;' +
    'line-height:1.2;font-size:.82rem;color:#94a3b8;text-decoration:none;cursor:pointer;font-family:inherit;transition:all .15s}' +
    '#quiz-bar .qb-item:hover{color:#38bdf8;background:rgba(56,189,248,0.06)}' +
    '#quiz-bar .qb-item:focus-visible{outline:2px solid #38bdf8;outline-offset:-2px}' +
    '#quiz-bar .qb-item.active{border-bottom-color:#38bdf8;color:#38bdf8;font-weight:700;background:rgba(56,189,248,0.1)}' +
    '#quiz-bar .qb-ic{display:block;font-size:1.15rem;line-height:1.25}' +
    '#quiz-bar .qb-en{display:block;font-size:.72rem;font-weight:500;color:#64748b;margin-top:2px}' +
    '#quiz-bar .qb-item.active .qb-en{color:#7dd3fc}' +
    '@media (min-width:1200px){#quiz-bar li{flex:0 0 auto}#quiz-bar .qb-item{width:auto;white-space:nowrap;padding:.6rem .8rem;font-size:.92rem}#quiz-bar .qb-ic{display:inline;font-size:inherit;margin-right:4px}#quiz-bar .qb-en{display:inline;margin-left:4px;font-size:.82rem}}';
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  var html = '<ul id="modeTabs">';
  items.forEach(function (it) {
    var label = '<span class="qb-ic" aria-hidden="true">' + it.icon + '</span> <span>' + it.de + (it.count ? ' (<span id="bookmarkTabCount">' + bookmarkCount() + '</span>)' : '') +
      '</span><span class="qb-en">' + it.vi + '</span>';
    var active = page === 'quiz' ? it.key === 'practice' : activeOnOtherPages[page] === it.key;
    if (it.mode && page === 'quiz') {
      html += '<li><button type="button" class="qb-item' + (active ? ' active' : '') + '" id="tab-' + it.key + '" data-mode="' + it.key +
        '"' + (active ? ' aria-current="true"' : '') + ' aria-controls="' + it.key + 'Options">' + label + '</button></li>';
    } else {
      var href = it.mode ? '/quiz.html#' + it.key : it.href;
      html += '<li><a class="qb-item' + (active ? ' active' : '') + '" href="' + href + '"' + (active ? ' aria-current="page"' : '') + '>' + label + '</a></li>';
    }
  });
  mount.innerHTML = html + '</ul>';
  mount.setAttribute('role', 'navigation');
  mount.setAttribute('aria-label', 'Quiz');

})();
