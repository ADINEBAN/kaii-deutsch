with open('swipe_flashcard.css', 'r', encoding='utf-8') as f:
    swipe_css = f.read()

for p in ['mobile/app.css', 'android-apk-project/app/src/main/assets/app.css']:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # Remove older duplicate .flashcard-inner and .flashcard-3d-scene blocks if needed or cleanly append
    c = c + '\n\n' + swipe_css
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(c)
    print('Updated CSS in', p)

