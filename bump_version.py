for p in ['mobile/app.js', 'android-apk-project/app/src/main/assets/app.js']:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace("const CURRENT_APP_VERSION = '1.0.0';", "const CURRENT_APP_VERSION = '1.0.2';")
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(c)
    print('Updated CURRENT_APP_VERSION to 1.0.2 in', p)

