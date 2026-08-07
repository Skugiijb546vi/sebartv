import requests
import re
html = requests.get('https://www.2embed.cc/embedtv/95479&s=1&e=1').text
matches = re.findall(r'https?://[^\s"\'<>]+', html)
for m in matches:
    if 'embed' in m or 'play' in m or 'skin' in m:
        print(m)
