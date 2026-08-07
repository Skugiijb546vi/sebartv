import requests
import re
import json

tmdb_id = '233643'
VIDSRC_BASE = 'https://vidsrc.hair'
embed_url = f'{VIDSRC_BASE}/embed/tv/{tmdb_id}/1/1'
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

html = session.get(embed_url).text
match = re.search(r'var Q = (\{.*?\});', html)
if match:
    print('Found Q token')
    q_data = json.loads(match.group(1))
    qs = f"type={q_data['type']}&id={q_data['id']}&s={q_data['s']}&e={q_data['e']}&t={q_data['t']}"
    
    sources_url = f'{VIDSRC_BASE}/api.php?a=sources&{qs}'
    print('Fetching sources:', sources_url)
    sources_resp = session.get(sources_url, headers={'Referer': embed_url}).json()
    print('Sources response:', sources_resp)
else:
    print('No Q token')
