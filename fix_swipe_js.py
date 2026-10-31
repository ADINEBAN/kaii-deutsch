import re

new_swipe_controller = """
  // ==========================================================================
  // Swipeable & 3D Flippable Flashcard Controller (Clean Separation)
  // ==========================================================================
  function initFlashcardSwipeGestures() {
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

    const stampPass = document.getElementById('stamp-pass');
    const stampFail = document.getElementById('stamp-fail');

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
        if (Math.abs(currentX) > 8 && Math.abs(currentX) > Math.abs(currentY)) {
          isHorizontal = true;
        } else if (Math.abs(currentY) > 10) {
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

      const elapsed = Date.now() - startTime;
      const dist = Math.abs(currentX);

      // Check if it's a Tap (very little movement, short duration) -> Flip Card!
      if (dist < 10 && Math.abs(currentY) < 10 && elapsed < 350) {
        resetSwipeWrap();
        state.flashcardFlipped = !state.flashcardFlipped;
        cardInner.classList.toggle('flipped', state.flashcardFlipped);
        return;
      }

      // Check if it's a valid swipe threshold
      if (isHorizontal && dist > 75) {
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
      } else {
        // Snap back to center
        resetSwipeWrap(true);
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
  }
"""

def update_js(p):
    with open(p, 'r', encoding='utf-8') as f:
        js = f.read()

    # Replace initFlashcardSwipeGestures implementation
    start = js.find('function initFlashcardSwipeGestures()')
    end = js.find('function nextFlashcard(known)')
    if start != -1 and end != -1:
        js = js[:start] + new_swipe_controller.strip() + '\n\n  ' + js[end:]
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        print('Updated swipe controller in', p)
    else:
        print('Could not find controller anchor in', p)

update_js('mobile/app.js')
update_js('android-apk-project/app/src/main/assets/app.js')

