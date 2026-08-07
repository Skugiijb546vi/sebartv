import requests
import re
import json

VIDSRC_BASE = 'https://vidsrc.hair'
tmdb_id = '969681'
embed_url = f'{VIDSRC_BASE}/embed/movie/{tmdb_id}'
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0', 'Referer': embed_url})

html = session.get(embed_url).text
match = re.search(r'var Q = (\{.*?\});', html)
if match:
    q = json.loads(match.group(1))
    qs = f"type={q['type']}&id={q['id']}&s={q['s']}&e={q['e']}&t={q['t']}"
    src_resp = session.get(f'{VIDSRC_BASE}/api.php?a=sources&{qs}').json()
    
    for server in src_resp['servers']:
        ref = server['ref']
        play_resp = session.get(f'{VIDSRC_BASE}/api.php?a=play&ref={ref}').json()
        url = play_resp.get('url')
        print('Server hash:', server.get('hash'), 'URL:', url)
        if url and url.startswith('/'):
            # Fetch the stream URL using the SAME session!
            stream_resp = session.get(f'{VIDSRC_BASE}{url}', allow_redirects=False)
            print('Status code:', stream_resp.status_code)
            if stream_resp.status_code in [301, 302]:
                print('Redirects to:', stream_resp.headers.get('Location'))
            else:
                print('Body:', stream_resp.text[:200])
