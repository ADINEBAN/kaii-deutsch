import re

swipe_js = """
  // ==========================================================================
  // Swipeable 3D Flashcard Interaction (Left = Fail, Right = Pass, Tap = Flip)
  // ==========================================================================
  function initFlashcardSwipeGestures() {
    const card = el.flashcardInner;
    if (!card) return;

    let startX = 0;
    let startY = 0;
    let currentX = 0;
    let currentY = 0;
    let isDragging = false;
    let isHorizontalSwipe = false;
    let startTime = 0;

    const stampPass = document.getElementById('stamp-pass');
    const stampFail = document.getElementById('stamp-fail');

    function onTouchStart(e) {
      if (e.target.closest('#card-speaker-btn')) return; // Ignore speaker button tap
      const touch = e.touches ? e.touches[0] : e;
      startX = touch.clientX;
      startY = touch.clientY;
      currentX = 0;
      currentY = 0;
      isDragging = true;
      isHorizontalSwipe = false;
      startTime = Date.now();
      card.style.transition = 'none';
      card.classList.add('swiping');
    }

    function onTouchMove(e) {
      if (!isDragging) return;
      const touch = e.touches ? e.touches[0] : e;
      currentX = touch.clientX - startX;
      currentY = touch.clientY - startY;

      // Lock swipe direction: if moving mostly vertically, allow native scroll
      if (!isHorizontalSwipe) {
        if (Math.abs(currentX) > 10 && Math.abs(currentX) > Math.abs(currentY)) {
          isHorizontalSwipe = true;
        } else if (Math.abs(currentY) > 10) {
          isDragging = false;
          resetCardVisuals();
          return;
        }
      }

      if (isHorizontalSwipe) {
        if (e.cancelable) e.preventDefault();

        // Calculate rotation and transform
        const rotateDeg = (currentX / 15) * (state.flashcardFlipped ? -1 : 1);
        const flipRotate = state.flashcardFlipped ? ' rotateY(180deg)' : '';
        card.style.transform = `translateX(${currentX}px) rotate(${rotateDeg}deg)${flipRotate}`;

        // Stamp opacity feedback
        const progress = Math.min(Math.abs(currentX) / 100, 1);
        if (currentX > 20) {
          // Swiping right (Đã nhớ)
          if (stampPass) stampPass.style.opacity = progress;
          if (stampFail) stampFail.style.opacity = 0;
        } else if (currentX < -20) {
          // Swiping left (Chưa thuộc)
          if (stampFail) stampFail.style.opacity = progress;
          if (stampPass) stampPass.style.opacity = 0;
        } else {
          if (stampPass) stampPass.style.opacity = 0;
          if (stampFail) stampFail.style.opacity = 0;
        }
      }
    }

    function onTouchEnd(e) {
      if (!isDragging && !isHorizontalSwipe) return;
      isDragging = false;
      card.classList.remove('swiping');

      const elapsed = Date.now() - startTime;
      const threshold = 85; // Pixels needed to register swipe

      if (isHorizontalSwipe && Math.abs(currentX) > threshold) {
        // Complete the swipe exit animation
        const isRightSwipe = currentX > 0;
        const exitX = isRightSwipe ? window.innerWidth + 200 : -window.innerWidth - 200;
        const exitRotate = isRightSwipe ? 25 : -25;
        const flipRotate = state.flashcardFlipped ? ' rotateY(180deg)' : '';

        card.style.transition = 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s';
        card.style.transform = `translateX(${exitX}px) rotate(${exitRotate}deg)${flipRotate}`;
        card.style.opacity = '0';

        setTimeout(() => {
          resetCardVisuals();
          nextFlashcard(isRightSwipe);
        }, 280);

      } else {
        // Snap back or Tap to Flip
        if (Math.abs(currentX) < 10 && Math.abs(currentY) < 10 && elapsed < 300) {
          // Tap: Toggle Flip
          state.flashcardFlipped = !state.flashcardFlipped;
          card.classList.toggle('flipped', state.flashcardFlipped);
        }
        resetCardVisuals(true);
      }
    }

    function resetCardVisuals(animate = false) {
      if (animate) {
        card.style.transition = 'transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.2s';
      } else {
        card.style.transition = '';
      }
      card.style.opacity = '1';
      card.style.transform = state.flashcardFlipped ? 'rotateY(180deg)' : 'none';
      if (stampPass) stampPass.style.opacity = 0;
      if (stampFail) stampFail.style.opacity = 0;
    }

    // Touch events
    card.addEventListener('touchstart', onTouchStart, { passive: true });
    card.addEventListener('touchmove', onTouchMove, { passive: false });
    card.addEventListener('touchend', onTouchEnd);
    card.addEventListener('touchcancel', () => resetCardVisuals(true));

    // Mouse drag support for desktop/testing
    card.addEventListener('mousedown', onTouchStart);
    window.addEventListener('mousemove', onTouchMove);
    window.addEventListener('mouseup', onTouchEnd);
  }
"""

def update_js(p):
    with open(p, 'r', encoding='utf-8') as f:
        js = f.read()

    # 1. Remove old click and button listeners
    old_listeners = """    // Flashcard events
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
    el.btnFail.addEventListener('click', () => nextFlashcard(false));"""

    new_listeners = """    // Flashcard events with full swipe gesture support
    initFlashcardSwipeGestures();

    el.cardSpeakerBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const current = state.flashcardList[state.flashcardIndex];
      if (current) playTTS(current.de);
    });

    if (el.btnPass) el.btnPass.addEventListener('click', () => nextFlashcard(true));
    if (el.btnFail) el.btnFail.addEventListener('click', () => nextFlashcard(false));"""

    if old_listeners in js:
        js = js.replace(old_listeners, new_listeners)
    else:
        # Replace individually if spacing differs
        js = js.replace("el.flashcardInner.addEventListener('click', () => {\n      state.flashcardFlipped = !state.flashcardFlipped;\n      el.flashcardInner.classList.toggle('flipped', state.flashcardFlipped);\n    });", "initFlashcardSwipeGestures();")
        js = js.replace("el.btnPass.addEventListener('click', () => nextFlashcard(true));", "if (el.btnPass) el.btnPass.addEventListener('click', () => nextFlashcard(true));")
        js = js.replace("el.btnFail.addEventListener('click', () => nextFlashcard(false));", "if (el.btnFail) el.btnFail.addEventListener('click', () => nextFlashcard(false));")

    # 2. Add initFlashcardSwipeGestures definition before nextFlashcard
    if 'function initFlashcardSwipeGestures()' not in js:
        anchor = '  function nextFlashcard(known) {'
        js = js.replace(anchor, swipe_js + '\n' + anchor)

    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print('Updated swipe JS in', p)

update_js('mobile/app.js')
update_js('android-apk-project/app/src/main/assets/app.js')
