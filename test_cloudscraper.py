import cloudscraper
import re
import json
import time

VIDSRC_BASE = 'https://vidsrc.hair'
tmdb_id = '95479'
embed_url = f'{VIDSRC_BASE}/embed/tv/{tmdb_id}/1/1'

scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})

print('Fetching main page...')
html = scraper.get(embed_url, headers={'Referer': 'https://vidsrc.hair/'}).text
match = re.search(r'var Q = (\{.*?\});', html)
if match:
    q = json.loads(match.group(1))
    qs = f"type={q['type']}&id={q['id']}&s={q['s']}&e={q['e']}&t={q['t']}"
    
    print('Polling API...')
    for i in range(10):
        src_resp = scraper.get(f'{VIDSRC_BASE}/api.php?a=sources&{qs}', headers={'Referer': embed_url}).json()
        status = src_resp.get('status')
        print(f'Attempt {i+1}:', status)
        if status == 'ok':
            print('Success!', src_resp)
            break
        time.sleep(2)
else:
    print('No Q token')
