import re
try:
    from curl_cffi import requests
except ImportError:
    print("curl_cffi not installed yet")
    exit(1)

try:
    res = requests.get('https://vidapi.xyz/embed/movie/tt0111161', impersonate='chrome110')
    print('Vidapi text length:', len(res.text))
    match = re.search(r'(https?://[^\s\"\'<>]+?\.m3u8)', res.text)
    print('M3U8 found:', match.group(1) if match else False)
except Exception as e:
    print('Error:', e)
