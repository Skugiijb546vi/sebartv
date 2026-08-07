import cloudscraper, re
scraper = cloudscraper.create_scraper()
res = scraper.get('https://vidapi.xyz/embed/movie/95')
html = res.text
print(html[:500])
for m in re.findall(r'<iframe.*?src=[\"\'](.*?)[\"\']', html):
    print('IFRAME:', m)
match = re.search(r'https?://[^\s\"\'\>]+?\.m3u8[^\s\"\'\>]*', html)
if match:
    print('M3U8:', match.group(0))
