import requests
import re
import json

VIDSRC_BASE = 'https://vidsrc.hair'
embed_url = f'{VIDSRC_BASE}/embed/movie/tt11904746'
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})
html = session.get(embed_url).text
match = re.search(r'var Q = (\{.*?\});', html)
if match:
    q = json.loads(match.group(1))
    qs = f"type={q['type']}&id={q['id']}&s={q['s']}&e={q['e']}&t={q['t']}"
    src_resp = session.get(f'{VIDSRC_BASE}/api.php?a=sources&{qs}', headers={'Referer': embed_url}).json()
    print('Movie status:', src_resp.get('status'))
else:
    print('No Q token')
