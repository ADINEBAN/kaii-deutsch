for p in ['mobile/app.js', 'android-apk-project/app/src/main/assets/app.js']:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace("const CURRENT_APP_VERSION = '1.0.2';", "const CURRENT_APP_VERSION = '1.0.3';")
    c = c.replace("const CURRENT_APP_VERSION = '1.0.0';", "const CURRENT_APP_VERSION = '1.0.3';")
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(c)
    print('Bumped version to 1.0.3 in', p)
