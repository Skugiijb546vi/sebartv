import sys
import re

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

if 'stream_with_context' not in code:
    code = code.replace('from flask import Flask, render_template, jsonify, request, make_response', 'from flask import Flask, render_template, jsonify, request, make_response, Response, stream_with_context\nfrom urllib.parse import urljoin, quote')

old_logic = '''                    else:
                        # Check if the stream server allows CORS
                        try:
                            head_resp = session.head(url, timeout=3)
                            cors = head_resp.headers.get('Access-Control-Allow-Origin', '')
                            if cors == '*' or cors != '':
                                return url, play_resp.get('type', 'hls'), servers
                            else:
                                if not fallback_url:
                                    fallback_url = url
                                    fallback_type = play_resp.get('type', 'hls')
                                continue
                        except Exception:
                            if not fallback_url:
                                fallback_url = url
                                fallback_type = play_resp.get('type', 'hls')
                            continue'''
new_logic = '''                    else:
                        return f'/api/proxy?url={quote(url)}', play_resp.get('type', 'hls'), servers'''

code = code.replace(old_logic, new_logic)

code = code.replace('return fallback_url, fallback_type, servers', 'return f\'/api/proxy?url={quote(fallback_url)}\', fallback_type, servers', 1)

proxy_route = '''
@app.route('/api/proxy')
def proxy_stream():
    url = request.args.get('url')
    if not url: return "No URL", 400
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://vidsrc.hair/'
    }
    try:
        r = requests.get(url, headers=headers, stream=True, timeout=10)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        resp_headers = [(name, value) for (name, value) in r.raw.headers.items() if name.lower() not in excluded_headers]
        resp_headers.append(('Access-Control-Allow-Origin', '*'))
        
        content_type = r.headers.get('Content-Type', '')
        
        if 'mpegurl' in content_type or url.endswith('.m3u8'):
            content = r.text
            new_lines = []
            for line in content.splitlines():
                line = line.strip()
                if not line: continue
                if line.startswith('#'):
                    if 'URI="' in line:
                        parts = line.split('URI="')
                        if len(parts) == 2:
                            uri_part = parts[1].split('"')[0]
                            abs_uri = urljoin(url, uri_part)
                            new_uri = f"/api/proxy?url={quote(abs_uri)}"
                            line = line.replace(f'URI="{uri_part}"', f'URI="{new_uri}"')
                    new_lines.append(line)
                else:
                    abs_url = urljoin(url, line)
                    new_lines.append(f'/api/proxy?url={quote(abs_url)}')
            return Response("\\n".join(new_lines), headers=resp_headers, content_type=content_type)
        else:
            return Response(stream_with_context(r.iter_content(chunk_size=1024*128)), headers=resp_headers, content_type=content_type)
    except Exception as e:
        return str(e), 500
'''

if 'def proxy_stream' not in code:
    code = code.replace('# --- Page Routes', proxy_route + '\n\n# --- Page Routes')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('Success!')
