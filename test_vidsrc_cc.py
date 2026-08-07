import requests

url = 'https://vidsrc.cc/v2/embed/tv/95479/1/1'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Referer': 'https://vidsrc.cc/',
}
resp = requests.get(url, headers=headers)
print('Status:', resp.status_code)
if resp.status_code == 200:
    print('Found m3u8:', '.m3u8' in resp.text)
