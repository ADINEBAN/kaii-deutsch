import os

def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find initFlashcardSwipeGestures line range
    swipe_start = -1
    swipe_end = -1
    for i, line in enumerate(lines):
        if 'function initFlashcardSwipeGestures()' in line:
            swipe_start = i
        if swipe_start != -1 and 'function nextFlashcard(known)' in line:
            swipe_end = i
            break

    assert swipe_start != -1 and swipe_end != -1, f"Swipe boundaries not found in {path}"

    new_swipe_code = """  function initFlashcardSwipeGestures() {
    const swipeWrap = document.getElementById('flashcard-swipe-wrap') || el.flashcardInner;
    const cardInner = el.flashcardInner;
    if (!swipeWrap || !cardInner) return;

    let startX = 0;
    let startY = 0;
    let currentX = 0;
    let currentY = 0;
    let isTouching = false;
    let isHorizontal = false;
    let startTime = 0;
    let lastFlipTime = 0;

    const stampPass = document.getElementById('stamp-pass');
    const stampFail = document.getElementById('stamp-fail');

    function toggleFlip() {
      if (Date.now() - lastFlipTime < 250) return;
      lastFlipTime = Date.now();
      state.flashcardFlipped = !state.flashcardFlipped;
      cardInner.classList.toggle('flipped', state.flashcardFlipped);
    }

    function onPointerDown(e) {
      if (e.target.closest('#card-speaker-btn')) return; // Allow audio button clicks
      const point = e.touches ? e.touches[0] : e;
      startX = point.clientX;
      startY = point.clientY;
      currentX = 0;
      currentY = 0;
      isTouching = true;
      isHorizontal = false;
      startTime = Date.now();
      swipeWrap.style.transition = 'none';
      swipeWrap.classList.add('swiping');
    }

    function onPointerMove(e) {
      if (!isTouching) return;
      const point = e.touches ? e.touches[0] : e;
      currentX = point.clientX - startX;
      currentY = point.clientY - startY;

      if (!isHorizontal) {
        if (Math.abs(currentX) > 10 && Math.abs(currentX) > Math.abs(currentY)) {
          isHorizontal = true;
        } else if (Math.abs(currentY) > 15) {
          isTouching = false;
          resetSwipeWrap();
          return;
        }
      }

      if (isHorizontal) {
        if (e.cancelable) e.preventDefault();

        const rotateDeg = currentX / 16;
        swipeWrap.style.transform = `translateX(${currentX}px) rotate(${rotateDeg}deg)`;

        const progress = Math.min(Math.abs(currentX) / 80, 1);
        if (currentX > 15) {
          if (stampPass) stampPass.style.opacity = progress;
          if (stampFail) stampFail.style.opacity = 0;
        } else if (currentX < -15) {
          if (stampFail) stampFail.style.opacity = progress;
          if (stampPass) stampPass.style.opacity = 0;
        } else {
          if (stampPass) stampPass.style.opacity = 0;
          if (stampFail) stampFail.style.opacity = 0;
        }
      }
    }

    function onPointerUp(e) {
      if (!isTouching) return;
      isTouching = false;
      swipeWrap.classList.remove('swiping');

      const dist = Math.abs(currentX);

      // 1. Swiped horizontally past threshold (65px) -> Next Card!
      if (isHorizontal && dist > 65) {
        const isRight = currentX > 0;
        const exitX = isRight ? (window.innerWidth + 250) : (-window.innerWidth - 250);
        const exitRotate = isRight ? 25 : -25;

        swipeWrap.style.transition = 'transform 0.28s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.28s';
        swipeWrap.style.transform = `translateX(${exitX}px) rotate(${exitRotate}deg)`;
        swipeWrap.style.opacity = '0';

        setTimeout(() => {
          resetSwipeWrap();
          nextFlashcard(isRight);
        }, 260);
        return;
      }

      // 2. Snap back to center
      resetSwipeWrap(true);

      // 3. If movement was small (< 30px), this was a Tap / Click -> FLIP CARD!
      if (dist < 30 && Math.abs(currentY) < 30) {
        toggleFlip();
      }
    }

    function resetSwipeWrap(animate = false) {
      if (animate) {
        swipeWrap.style.transition = 'transform 0.32s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s';
      } else {
        swipeWrap.style.transition = '';
      }
      swipeWrap.style.transform = '';
      swipeWrap.style.opacity = '1';
      if (stampPass) stampPass.style.opacity = 0;
      if (stampFail) stampFail.style.opacity = 0;
    }

    // Touch events
    swipeWrap.addEventListener('touchstart', onPointerDown, { passive: true });
    swipeWrap.addEventListener('touchmove', onPointerMove, { passive: false });
    swipeWrap.addEventListener('touchend', onPointerUp);
    swipeWrap.addEventListener('touchcancel', () => resetSwipeWrap(true));

    // Desktop mouse events
    swipeWrap.addEventListener('mousedown', onPointerDown);
    window.addEventListener('mousemove', onPointerMove);
    window.addEventListener('mouseup', onPointerUp);

    // Click fallback on inner card
    cardInner.addEventListener('click', (e) => {
      if (e.target.closest('#card-speaker-btn')) return;
      if (Math.abs(currentX) < 15) {
        toggleFlip();
      }
    });
  }
\n"""

    # Replace swipe section
    lines = lines[:swipe_start] + [new_swipe_code] + lines[swipe_end:]

    # Find showMatchWin line range
    match_start = -1
    match_end = -1
    for i, line in enumerate(lines):
        if 'function showMatchWin()' in line:
            match_start = i
        if match_start != -1 and 'function initQuizDeVi()' in line:
            match_end = i
            break

    assert match_start != -1 and match_end != -1, f"Match boundaries not found in {path}"

    new_match_code = """  let matchStreak = 0;

  function showMatchWin() {
    matchStreak++;
    state.matchLocked = true;

    // Highlight all matched tiles with celebration effect
    const tiles = el.matchGrid.querySelectorAll('.match-tile');
    tiles.forEach(t => {
      t.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
      t.style.transform = 'scale(1.05)';
      t.style.borderColor = '#22c55e';
      t.style.boxShadow = '0 0 20px rgba(34, 197, 94, 0.6)';
    });

    showToast(`🎉 Xuất sắc! Ván ${matchStreak} thành công! Đang tải 6 cặp từ mới...`);

    // Automatically transition to new round after 850ms without pressing any button
    setTimeout(() => {
      tiles.forEach(t => {
        t.style.transform = 'scale(0.85)';
        t.style.opacity = '0';
      });
      setTimeout(() => {
        initMatchGame();
      }, 250);
    }, 850);
  }
\n"""

    # Replace match section
    lines = lines[:match_start] + [new_match_code] + lines[match_end:]

    content = ''.join(lines)
    # Bump version to 1.0.5
    content = content.replace("const CURRENT_APP_VERSION = '1.0.4';", "const CURRENT_APP_VERSION = '1.0.5';")
    content = content.replace("const CURRENT_APP_VERSION = '1.0.3';", "const CURRENT_APP_VERSION = '1.0.5';")

    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"Patched {path} successfully! Total lines: {len(lines)}")

patch_file('mobile/app.js')

