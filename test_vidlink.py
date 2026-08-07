import cloudscraper
import re

scraper = cloudscraper.create_scraper()
res = scraper.get('https://vidlink.pro/movie/95')
html = res.text

match = re.search(r'https?://[^\s"\'\>]+?\.m3u8[^\s"\'\>]*', html)
if match:
    print('FOUND M3U8:', match.group(0))
else:
    print('NO M3U8 in HTML. Finding APIs...')
    for m in re.findall(r'/api/[a-zA-Z0-9_\-\/]+', html):
        print(m)
