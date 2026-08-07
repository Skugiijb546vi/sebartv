import requests
import re
import json

VIDSRC_BASE = 'https://vidsrc.hair'
tmdb_id = '969681'
embed_url = f'{VIDSRC_BASE}/embed/movie/{tmdb_id}'
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

html = session.get(embed_url).text
match = re.search(r'var Q = (\{.*?\});', html)
if match:
    q = json.loads(match.group(1))
    qs = f"type={q['type']}&id={q['id']}&s={q['s']}&e={q['e']}&t={q['t']}"
    src_resp = session.get(f'{VIDSRC_BASE}/api.php?a=sources&{qs}', headers={'Referer': embed_url}).json()
    ref = src_resp['servers'][0]['ref']
    play_resp = session.get(f'{VIDSRC_BASE}/api.php?a=play&ref={ref}', headers={'Referer': embed_url}).json()
    
    url = play_resp.get('url')
    print('Got URL:', url)
    if url.startswith('/'):
        stream_resp = session.get(f'{VIDSRC_BASE}{url}', headers={'Referer': embed_url})
        print('Stream status:', stream_resp.status_code)
        print('Stream content:', stream_resp.text[:500])
