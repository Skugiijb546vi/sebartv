import os

# Fix app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

# Replace the play_resp logic
old_logic = '''                if play_resp.get('url'):
                    return play_resp['url'], play_resp.get('type', 'hls'), servers'''

new_logic = '''                if play_resp.get('url'):
                    url = play_resp['url']
                    if url.startswith('/'):
                        url = f"{VIDSRC_BASE}{url}"
                    return url, play_resp.get('type', 'hls'), servers'''

if old_logic in app_code:
    app_code = app_code.replace(old_logic, new_logic)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    print("Fixed app.py")
else:
    print("Could not find old_logic in app.py")

# Fix index.html
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

bad_link = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/hls.js@1.5.13/dist/hls.min.js">'
if bad_link in html:
    html = html.replace(bad_link, '')
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Fixed index.html")
else:
    print("Could not find bad_link in index.html")
