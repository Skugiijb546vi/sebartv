import os
import re

with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

old_logic = '''        for server in servers:
            try:
                ref = server['ref']
                play_url = f'{VIDSRC_BASE}/api.php?a=play&ref={ref}'
                play_resp = session.get(
                    play_url, headers={'Referer': embed_url}, timeout=10
                ).json()

                if play_resp.get('url'):
                    url = play_resp['url']
                    if url.startswith('/'):
                        url = f"{VIDSRC_BASE}{url}"
                    return url, play_resp.get('type', 'hls'), servers
            except Exception:
                continue

        return None, None, servers'''

new_logic = '''        fallback_url = None
        fallback_type = None

        for server in servers:
            try:
                ref = server['ref']
                play_url = f'{VIDSRC_BASE}/api.php?a=play&ref={ref}'
                play_resp = session.get(
                    play_url, headers={'Referer': embed_url}, timeout=10
                ).json()

                url = play_resp.get('url')
                if url:
                    if url.startswith('/'):
                        url = f"{VIDSRC_BASE}{url}"
                        
                    if '/_stream' in url:
                        if not fallback_url:
                            fallback_url = url
                            fallback_type = play_resp.get('type', 'hls')
                    else:
                        return url, play_resp.get('type', 'hls'), servers
            except Exception:
                continue
                
        if fallback_url:
            return fallback_url, fallback_type, servers

        return None, None, servers'''

if old_logic in app_code:
    app_code = app_code.replace(old_logic, new_logic)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(app_code)
    print("Fixed server prioritization in app.py")
else:
    print("Could not find old logic in app.py")
