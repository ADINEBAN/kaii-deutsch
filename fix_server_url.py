import os

def update_clean_url(p):
    with open(p, 'r', encoding='utf-8') as f:
        t = f.read()

    old_var = "let SERVER_BASE_URL = localStorage.getItem('kaii_server_ip') || 'http://192.168.1.5:8080';"
    new_var = "let SERVER_BASE_URL = (localStorage.getItem('kaii_server_ip') || 'http://192.168.1.5:8080').replace(/\\/m\\/?$/, '').replace(/\\/+$/, '');"

    if old_var in t:
        t = t.replace(old_var, new_var)

    old_prompt_clean = "SERVER_BASE_URL = newIp.trim().replace(/\\/+$/, '');"
    new_prompt_clean = "SERVER_BASE_URL = newIp.trim().replace(/\\/m\\/?$/, '').replace(/\\/+$/, '');"
    if old_prompt_clean in t:
        t = t.replace(old_prompt_clean, new_prompt_clean)

    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(t)
    print('Updated clean URL in', p)

update_clean_url('mobile/app.js')
update_clean_url('android-apk-project/app/src/main/assets/app.js')

