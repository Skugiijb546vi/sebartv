import cloudscraper, re
scraper = cloudscraper.create_scraper()
res = scraper.get('https://autoembed.co/movie/imdb/tt0120591')
html = res.text
print('autoembed HTML:', html[:100])
match = re.search(r'https?://[^\s"\'\>]+?\.m3u8[^\s"\'\>]*', html)
if match:
    print('M3U8:', match.group(0))
for m in re.findall(r'<iframe.*?src=["\'](.*?)["\']', html):
    print('IFRAME:', m)
