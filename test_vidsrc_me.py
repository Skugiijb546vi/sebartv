import requests
import re
url = 'https://vidsrc.me/embed/tv?tmdb=95479&season=1&episode=1'
html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
if 'rcp.vidsrc.me' in html: print('Found rcp.vidsrc.me')
if 'vidsrc.stream' in html: print('Found vidsrc.stream')
if '.m3u8' in html: print('Found .m3u8')
print('Looking for URLs...')
matches = re.findall(r'https?://[^"\'\s<>]+', html)
for m in set(matches):
    if 'vidsrc' in m:
        print(m)
