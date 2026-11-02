import re

def update_css(path):
    with open(path, 'r', encoding='utf-8') as f:
        css = f.read()

    old_target = """/* Wrapper for swipe & drag (moves horizontally and rotates) */
.flashcard-swipe-wrap {
  position: relative;
  width: 100%;
  height: 100%;
  will-change: transform, opacity;
  cursor: grab;
}

.flashcard-swipe-wrap.swiping {
  cursor: grabbing;
}

/* Inner 3D card for 180deg flip (pure 3D flipping only) */
.flashcard-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
}

.flashcard-inner.flipped {
  transform: rotateY(180deg);
}

.flashcard-face {
  position: absolute;
  inset: 0;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  border-radius: 24px;
  padding: 24px 20px;
  background: var(--glass-card);
  backdrop-filter: blur(24px) saturate(200%);
  -webkit-backdrop-filter: blur(24px) saturate(200%);
  border: 1px solid var(--glass-border);
  box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
}

.flashcard-back {
  transform: rotateY(180deg);
  background: rgba(22, 34, 62, 0.88);
  border-color: rgba(59, 130, 246, 0.35);
}"""

    new_replacement = """/* Wrapper for swipe & drag (moves horizontally and rotates) */
.flashcard-swipe-wrap {
  position: relative;
  width: 100%;
  height: 100%;
  will-change: transform, opacity;
  cursor: grab;
  transform-style: preserve-3d;
  -webkit-transform-style: preserve-3d;
}

.flashcard-swipe-wrap.swiping {
  cursor: grabbing;
}

/* Inner 3D card for 180deg flip (pure 3D flipping only) */
.flashcard-inner {
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.45s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
  -webkit-transform-style: preserve-3d;
  cursor: pointer;
}

.flashcard-inner.flipped {
  transform: rotateY(180deg);
  -webkit-transform: rotateY(180deg);
}

.flashcard-face {
  position: absolute;
  inset: 0;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  border-radius: 24px;
  padding: 24px 20px;
  background: var(--glass-card);
  backdrop-filter: blur(24px) saturate(200%);
  -webkit-backdrop-filter: blur(24px) saturate(200%);
  border: 1px solid var(--glass-border);
  box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  transition: opacity 0.2s ease, visibility 0.2s ease;
}

.flashcard-front {
  transform: rotateY(0deg);
  -webkit-transform: rotateY(0deg);
  z-index: 2;
}

.flashcard-back {
  transform: rotateY(180deg);
  -webkit-transform: rotateY(180deg);
  background: rgba(22, 34, 62, 0.95);
  border-color: rgba(59, 130, 246, 0.45);
  z-index: 1;
}

/* Guaranteed display states for Android WebView */
.flashcard-inner.flipped .flashcard-front {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  z-index: 1;
}

.flashcard-inner.flipped .flashcard-back {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  z-index: 2;
}

.flashcard-inner:not(.flipped) .flashcard-back {
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  z-index: 1;
}

.flashcard-inner:not(.flipped) .flashcard-front {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  z-index: 2;
}"""

    if old_target in css:
        css = css.replace(old_target, new_replacement)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(css)
        print("Updated CSS in:", path)
    else:
        print("Target not found in CSS:", path)

update_css('mobile/app.css')
update_css('android-apk-project/app/src/main/assets/app.css')

