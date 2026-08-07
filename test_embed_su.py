import requests
import re
url = 'https://embed.su/embed/tv/95479/1/1'
try:
    html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).text
    print('Length:', len(html))
    print('.m3u8 found?', '.m3u8' in html)
    matches = re.findall(r'https?://[^\s\"\'<>]+', html)
    for m in set(matches):
        if 'api' in m or '.su' in m:
            print(m)
except Exception as e:
    print('Failed', e)
