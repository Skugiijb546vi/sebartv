import cloudscraper, re
scraper = cloudscraper.create_scraper()
res = scraper.get('https://vidsrc.pm/embed/movie?tmdb=95')
html = res.text
print('serversList?', 'serversList' in html)
match = re.search(r'https?://[^\s"\'\>]+?\.m3u8[^\s"\'\>]*', html)
if match:
    print('M3U8:', match.group(0))
else:
    print('No m3u8')
