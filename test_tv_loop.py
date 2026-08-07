import requests
import re
import json
import time

VIDSRC_BASE = 'https://vidsrc.hair'
tmdb_id = '95479'
embed_url = f'{VIDSRC_BASE}/embed/tv/{tmdb_id}/1/1'
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0', 'Referer': embed_url})

html = session.get(embed_url).text
match = re.search(r'var Q = (\{.*?\});', html)
if match:
    q = json.loads(match.group(1))
    qs = f"type={q['type']}&id={q['id']}&s={q['s']}&e={q['e']}&t={q['t']}"
    
    for _ in range(5):
        src_resp = session.get(f'{VIDSRC_BASE}/api.php?a=sources&{qs}').json()
        print('Sources status:', src_resp.get('status'))
        if src_resp.get('status') == 'ok':
            break
        time.sleep(2)
        
    if src_resp.get('status') == 'ok':
        for server in src_resp.get('servers', []):
            print('Server:', server.get('hash'))
            ref = server['ref']
            play_resp = session.get(f'{VIDSRC_BASE}/api.php?a=play&ref={ref}').json()
            print('Play URL:', play_resp.get('url'))
else:
    print('No Q token found')
