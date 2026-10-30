import sys

def main():
    # 1. Update index.html
    with open('mobile/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    html = html.replace('/mobile/manifest.json', 'manifest.json')
    html = html.replace('/icons/kaii_192.png', 'icons/kaii_192.png')
    html = html.replace('/mobile/app.css?v=3.5', 'app.css')
    html = html.replace('/mobile/icons.js?v=3.5', 'icons.js')
    html = html.replace('/mobile/app.js?v=3.5', 'app.js')
    html = html.replace('/mobile/avatar_square.jpg?v=3.5', 'avatar_square.jpg')

    with open('android-apk-project/app/src/main/assets/index.html', 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print("Clean index.html written.")

    # 2. Update app.js
    with open('mobile/app.js', 'r', encoding='utf-8') as f:
        js = f.read()

    js = js.replace("'/words_final.json'", "'words_final.json'")
    js = js.replace("'/conjugations.json'", "'conjugations.json'")
    js = js.replace("'/sentences_final.json'", "'sentences_final.json'")
    js = js.replace("'/grammar_summary.json'", "'grammar_summary.json'")
    js = js.replace("'/mobile/sw.js?v=3.6'", "'sw.js'")

    with open('android-apk-project/app/src/main/assets/app.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print("Clean app.js written.")

if __name__ == '__main__':
    main()

