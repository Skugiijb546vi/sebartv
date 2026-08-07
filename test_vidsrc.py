import requests
import re
import json

VIDSRC_BASE = 'https://vidsrc.hair'
embed_url = f'{VIDSRC_BASE}/embed/movie/tt0113117'
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
})
html = session.get(embed_url, timeout=10).text
match = re.search(r'var Q = (\{.*?\});', html)
if not match:
    print('No Q token. length:', len(html))
else:
    q_data = json.loads(match.group(1))
    qs = f"type={q_data['type']}&id={q_data['id']}&s={q_data['s']}&e={q_data['e']}&t={q_data['t']}"
    src_resp = session.get(f'{VIDSRC_BASE}/api.php?a=sources&' + qs, headers={'Referer': embed_url}).json()
    print('Status:', src_resp)
