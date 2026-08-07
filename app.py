"""
ZEDFLIX — Movie Streaming Platform
Backend API Server (Flask)
"""

from flask import Flask, render_template, jsonify, request, make_response, Response, stream_with_context
from urllib.parse import urljoin, quote
import requests
import re
import json
import os
import random

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.after_request
def add_header(r):
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    return r

TMDB_API_KEY = '15d2ea6d0dc1d476efbca3eba2b9bbfb'
TMDB_BASE = 'https://api.themoviedb.org/3'
VIDSRC_BASE = 'https://vidsrc.hair'

def tmdb_get(path, params=None):
    p = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
    if params:
        p.update(params)
    try:
        r = requests.get(f'{TMDB_BASE}{path}', params=p, timeout=8)
        return r.json()
    except Exception:
        return {}

def get_imdb_id(tmdb_id, media_type='movie'):
    data = tmdb_get(f'/{media_type}/{tmdb_id}/external_ids')
    return data.get('imdb_id', '')

def format_movie(m, media_type='movie'):
    return {
        'id': m.get('id'),
        'media_type': media_type,
        'title': m.get('title', m.get('name', '')),
        'poster': f"https://image.tmdb.org/t/p/w500{m['poster_path']}" if m.get('poster_path') else '',
        'backdrop': f"https://image.tmdb.org/t/p/w1280{m['backdrop_path']}" if m.get('backdrop_path') else '',
        'overview': m.get('overview', ''),
        'rating': m.get('vote_average', 0),
        'year': (m.get('release_date') or m.get('first_air_date', ''))[:4],
    }

PROVIDERS = [
    'https://vidsrc.hair', 'https://vidsrc.to', 'https://vidsrc.me', 'https://vidsrc.net',
    'https://vidsrc.pro', 'https://vidsrc.in', 'https://vidsrc.pm', 'https://vidsrc.xyz',
    'https://vidsrc.nl', 'https://vidsrc.su', 'https://vidsrc.ru', 'https://vidsrc.pw',
    'https://vidsrc.vip', 'https://vidsrc.app', 'https://vidsrc.cc', 'https://vidsrc.gg',
    'https://vidsrc.io', 'https://vidsrc.co', 'https://vidsrc.tv', 'https://vidsrc.club',
    'https://vidsrc.one', 'https://vidsrc.us', 'https://vidsrc.ws', 'https://vidsrc.uk',
    'https://vidsrc.bz', 'https://vidsrc.la', 'https://vidsrc.vc', 'https://vidsrc.click',
    'https://vidsrc.online', 'https://vidsrc.rest', 'https://vidsrc.live', 'https://vidsrc.icu',
    'https://vidsrc.site', 'https://vidsrc.website', 'https://vidsrc.space', 'https://vidsrc.tech',
    'https://vidsrc.store', 'https://vidsrc.fun', 'https://vidsrc.stream', 'https://vidsrc.cloud'
]

FAST_PROVIDERS = [
    'https://vidsrc.hair', 'https://vidsrc.to', 'https://vidsrc.me', 'https://vidsrc.in', 'https://vidsrc.net'
]

import concurrent.futures

def fetch_provider_servers(provider, imdb_id, media_type, season, episode):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    try:
        if media_type == 'movie':
            embed_url = f'{provider}/embed/movie/{imdb_id}'
        else:
            embed_url = f'{provider}/embed/tv/{imdb_id}/{season}/{episode}'
            
        html = session.get(embed_url, timeout=7).text
        match = re.search(r'var Q = (\{.*?\});', html)
        if not match: return []
        
        q_data = json.loads(match.group(1))
        qs = f"type={q_data['type']}&id={q_data['id']}&s={q_data['s']}&e={q_data['e']}&t={q_data['t']}"
        sources_url = f'{provider}/api.php?a=sources&{qs}'
        sources_resp = session.get(sources_url, headers={'Referer': embed_url}, timeout=7).json()
        
        if sources_resp.get('status') == 'ok':
            servers = sources_resp.get('servers', [])
            for s in servers:
                s['provider'] = provider
            return servers
    except:
        pass
    return []

def extract_stream(imdb_id, media_type='movie', season=1, episode=1):
    all_servers = []
    
    # Always include the primary provider, plus 2 random ones to ensure reliability
    selected_providers = [FAST_PROVIDERS[0]] + random.sample(FAST_PROVIDERS[1:], 2)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(fetch_provider_servers, p, imdb_id, media_type, season, episode) for p in selected_providers]
        for future in concurrent.futures.as_completed(futures):
            servers = future.result()
            if servers:
                all_servers.extend(servers)
            
    unique_servers = []
    seen_names = set()
    for s in all_servers:
        name = s.get('name')
        if name and name not in seen_names:
            seen_names.add(name)
            unique_servers.append(s)
            
    if not unique_servers:
        return None, None, [], []
        
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site'
    })
    
    for server in unique_servers:
        try:
            ref = server['ref']
            provider = server.get('provider', PROVIDERS[0])
            play_url = f'{provider}/api.php?a=play&ref={ref}'
            play_resp = session.get(play_url, headers={'Referer': f'{provider}/'}, timeout=10).json()

            if play_resp.get('url'):
                url = play_resp['url']
                subs = play_resp.get('subtitles') or play_resp.get('tracks') or play_resp.get('subs') or play_resp.get('captions') or []
                return url, play_resp.get('type', 'hls'), subs, unique_servers
        except:
            continue
            
    return None, None, [], unique_servers

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/play/<media_type>/<int:tmdb_id>')
def play_media(media_type, tmdb_id):
    imdb_id = get_imdb_id(tmdb_id, media_type)
    if not imdb_id:
        return jsonify({'error': 'IMDB ID not found'}), 404

    season = request.args.get('s', 1, type=int)
    episode = request.args.get('e', 1, type=int)

    stream_url, stream_type, subtitles, servers = extract_stream(imdb_id, media_type, season, episode)
    
    # Merge with reliable Stremio subtitles
    stremio_subs = fetch_stremio_subs(media_type, imdb_id, season, episode)
    subtitles = stremio_subs + subtitles
    
    if stream_url:
        return jsonify({
            'success': True,
            'stream_url': stream_url,
            'stream_type': stream_type,
            'subtitles': subtitles,
            'server_count': len(servers),
            'servers': servers
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Could not extract direct stream link from backend',
            'server_count': len(servers),
        })

@app.route('/api/play_server/<ref>')
def play_server(ref):
    provider = request.args.get('provider', PROVIDERS[0])
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    try:
        play_url = f'{provider}/api.php?a=play&ref={ref}'
        play_resp = session.get(play_url, headers={'Referer': f'{provider}/'}, timeout=10).json()
        if play_resp.get('url'):
            subs = play_resp.get('subtitles') or play_resp.get('tracks') or play_resp.get('subs') or play_resp.get('captions') or []
            
            # Since play_server doesn't have media_type natively passed, we rely on frontend sending it if we want
            # But the primary stream already loads subtitles, so this is just in case.
            
            return jsonify({
                'success': True,
                'stream_url': play_resp['url'],
                'stream_type': play_resp.get('type', 'hls'),
                'subtitles': subs
            })
    except Exception as e:
        print(f"Error extracting server {ref}: {e}")
    
    return jsonify({'success': False})

@app.route('/api/genres')
def genres():
    data = tmdb_get('/genre/movie/list')
    return jsonify(data.get('genres', []))

@app.route('/api/genre/<int:genre_id>')
def genre_movies(genre_id):
    data = tmdb_get('/discover/movie', {
        'with_genres': genre_id,
        'sort_by': 'popularity.desc',
    })
    return jsonify([format_movie(m, 'movie') for m in data.get('results', [])[:20]])

@app.route('/api/explore/<category>')
def explore_category(category):
    page = request.args.get('page', 1, type=int)
    params = {
        'sort_by': 'popularity.desc',
        'page': page
    }
    
    if category == 'movies':
        endpoint = '/discover/movie'
        media_type = 'movie'
    elif category == 'tv':
        endpoint = '/discover/tv'
        media_type = 'tv'
    elif category == 'documentary':
        endpoint = '/discover/movie'
        params['with_genres'] = 99
        media_type = 'movie'
    elif category == 'anime':
        endpoint = '/discover/tv'
        params['with_genres'] = 16
        params['with_original_language'] = 'ja'
        media_type = 'tv'
    else:
        return jsonify([])
        
    data = tmdb_get(endpoint, params)
    return jsonify([format_movie(m, media_type) for m in data.get('results', [])])

def fetch_stremio_subs(media_type, imdb_id, season=1, episode=1):
    try:
        stremio_url = f'https://opensubtitles-v3.strem.io/subtitles/{media_type}/{imdb_id}'
        if media_type == 'tv':
            stremio_url += f':{season}:{episode}'
        stremio_url += '.json'
        
        st_resp = requests.get(stremio_url, timeout=5).json()
        subs = []
        if 'subtitles' in st_resp:
            seen_langs = set()
            english_url = None
            
            for sub in st_resp['subtitles']:
                lang = sub.get('lang', 'unk')
                sub_url = sub.get('url')
                
                # Save first english sub for AI translation
                if (lang.lower() == 'eng' or lang.lower() == 'english') and not english_url:
                    english_url = sub_url
                    
                if lang not in seen_langs:
                    seen_langs.add(lang)
                    subs.append({
                        'label': lang,
                        'file': f"/api/sub/vtt?url={requests.utils.quote(sub_url)}"
                    })
                    
            # Inject AI Translated Kurdish
            if english_url:
                subs.insert(0, {
                    'label': 'Kurdish (AI Translated)',
                    'file': f"/api/sub/vtt/kurdish?url={requests.utils.quote(english_url)}"
                })
                
        return subs
    except Exception as e:
        print("Stremio sub error:", e)
        return []

@app.route('/api/sub/vtt')
def proxy_vtt():
    srt_url = request.args.get('url')
    if not srt_url: return "No URL", 400
    try:
        resp = requests.get(srt_url, timeout=5)
        text = resp.text
        # Convert SRT to VTT
        vtt = "WEBVTT\n\n" + text.replace(',', '.')
        return Response(vtt, mimetype='text/vtt')
    except Exception as e:
        return str(e), 500

@app.route('/api/sub/vtt/kurdish')
def proxy_vtt_kurdish():
    srt_url = request.args.get('url')
    if not srt_url: return "No URL", 400
    try:
        resp = requests.get(srt_url, timeout=5)
        text = resp.text.replace('\r', '') # Normalize line endings
        
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='auto', target='ckb')
        
        blocks = text.strip().split('\n\n')
        new_blocks = []
        texts_to_translate = []
        
        # Extract texts
        for block in blocks:
            lines = block.split('\n')
            if len(lines) >= 3:
                texts_to_translate.append('\n'.join(lines[2:]))
            else:
                texts_to_translate.append('')
                
        # Chunk the texts
        chunks = []
        current_chunk = []
        current_len = 0
        
        for t in texts_to_translate:
            if not t:
                # We still need placeholders to maintain structure
                current_chunk.append('')
                continue
                
            if current_len + len(t) > 4000:
                chunks.append(current_chunk)
                current_chunk = []
                current_len = 0
                
            if len(t) > 4000:
                t = t[:4000]
                
            current_chunk.append(t)
            current_len += len(t) + 5
            
        if current_chunk:
            chunks.append(current_chunk)
            
        def translate_chunk_group(c_group):
            if not any(c_group): return c_group
            combined = ' ||| '.join(c_group)
            try:
                res = translator.translate(combined)
                res = res.replace('| | |', '|||').replace(' | | ', '|||')
                translated = [x.strip() for x in res.split('|||')]
                # Pad if mismatch
                if len(translated) < len(c_group):
                    translated.extend([''] * (len(c_group) - len(translated)))
                return translated[:len(c_group)]
            except Exception as ex:
                print("Chunk error:", repr(ex))
                return c_group

        import concurrent.futures
        translated_texts = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            # Map over chunks concurrently
            results = list(executor.map(translate_chunk_group, chunks))
            
        for r in results:
            translated_texts.extend(r)
            
        # Rebuild
        for i, block in enumerate(blocks):
            lines = block.split('\n')
            if len(lines) >= 3:
                new_text = translated_texts[i] if i < len(translated_texts) else '\n'.join(lines[2:])
                new_block = '\n'.join(lines[:2]) + '\n' + new_text
                new_blocks.append(new_block)
            else:
                new_blocks.append(block)
                
        vtt = "WEBVTT\n\n" + '\n\n'.join(new_blocks).replace(',', '.')
        return Response(vtt, mimetype='text/vtt')
    except Exception as e:
        print("Translate error:", repr(e))
        # Fallback to original if translation fails entirely
        vtt = "WEBVTT\n\n" + text.replace(',', '.')
        return Response(vtt, mimetype='text/vtt')

@app.route('/api/subtitles/<media_type>/<int:tmdb_id>')
def get_subtitles(media_type, tmdb_id):
    season = request.args.get('s', 1)
    episode = request.args.get('e', 1)
    try:
        # Get IMDB ID
        ext = tmdb_get(f'/{media_type}/{tmdb_id}/external_ids')
        imdb_id = ext.get('imdb_id')
        if not imdb_id: return jsonify([])
        
        # Fetch from Stremio OpenSubtitles v3
        stremio_url = f'https://opensubtitles-v3.strem.io/subtitles/{media_type}/{imdb_id}'
        if media_type == 'tv':
            stremio_url += f':{season}:{episode}'
        stremio_url += '.json'
        
        st_resp = requests.get(stremio_url, timeout=5).json()
        subs = []
        if 'subtitles' in st_resp:
            seen_langs = set()
            for sub in st_resp['subtitles']:
                lang = sub.get('lang', 'unk')
                if lang not in seen_langs:
                    seen_langs.add(lang)
                    # Point to our VTT proxy
                    subs.append({
                        'label': lang,
                        'file': f"/api/sub/vtt?url={requests.utils.quote(sub.get('url'))}"
                    })
        return jsonify(subs)
    except Exception as e:
        print("Subtitle error:", e)
        return jsonify([])

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "Missing URL", 400
        
    provider = request.args.get('provider', 'https://vidsrc.hair')
    if not provider.endswith('/'):
        provider += '/'
        
    import random
    random_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': provider,
        'Origin': provider.rstrip('/'),
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'X-Forwarded-For': random_ip,
        'X-Real-IP': random_ip
    }
    
    range_header = request.headers.get('Range', None)
    try:
        import cloudscraper
        scraper = cloudscraper.create_scraper(browser='chrome')
        if range_header:
            headers['Range'] = range_header
            resp = scraper.get(url, headers=headers, stream=True, timeout=15)
        else:
            resp = scraper.get(url, headers=headers, stream=True, timeout=15)
        content_type = resp.headers.get('Content-Type', '').lower()
        is_playlist = 'application/vnd.apple.mpegurl' in content_type or url.endswith('.m3u8') or url.endswith('.txt')
        
        if is_playlist:
            text = resp.text
            lines = text.split('\n')
            new_lines = []
            base_url = url.rsplit('/', 1)[0] + '/'
            
            def rewrite_url(u):
                if not u.startswith('http'):
                    u = urljoin(url, u)
                # Let the browser fetch video chunks directly to prevent proxy 429 rate limits!
                if '.ts' in u or '.mp4' in u or '.m4s' in u:
                    return u
                return f"/proxy?url={quote(u)}&provider={quote(provider)}"
                
            for line in lines:
                line = line.strip()
                if line:
                    if line.startswith('#'):
                        # Rewrite URI="xxx" inside tags
                        line = re.sub(r'URI="([^"]+)"', lambda m: f'URI="{rewrite_url(m.group(1))}"', line)
                    else:
                        line = rewrite_url(line)
                new_lines.append(line)
            return Response('\n'.join(new_lines), mimetype='application/vnd.apple.mpegurl')
            
        def generate():
            try:
                for chunk in resp.iter_content(chunk_size=131072):
                    if chunk:
                        yield chunk
            finally:
                resp.close()
                    
        proxy_resp = Response(stream_with_context(generate()), status=resp.status_code, content_type=resp.headers.get('Content-Type', 'video/MP2T'))
        
        for key in ['Content-Length', 'Content-Range', 'Accept-Ranges']:
            if key in resp.headers:
                proxy_resp.headers[key] = resp.headers[key]
                
        proxy_resp.headers['Access-Control-Allow-Origin'] = '*'
        return proxy_resp
        
    except Exception as e:
        print(f"Proxy error for {url}: {e}")
        return str(e), 500

@app.route('/api/trending')
def trending():
    data = tmdb_get('/trending/all/day')
    return jsonify([format_movie(m, m.get('media_type', 'movie')) for m in data.get('results', [])[:20]])

@app.route('/api/anime')
def anime():
    data = tmdb_get('/discover/tv', {'with_genres': '16', 'with_original_language': 'ja', 'sort_by': 'popularity.desc'})
    return jsonify([format_movie(m, 'tv') for m in data.get('results', [])[:20]])

@app.route('/api/drama')
def drama():
    data = tmdb_get('/discover/tv', {'with_genres': '18', 'with_original_language': 'ko', 'sort_by': 'popularity.desc'})
    return jsonify([format_movie(m, 'tv') for m in data.get('results', [])[:20]])

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    data = tmdb_get('/search/multi', {'query': query})
    results = [format_movie(m, m.get('media_type', 'movie')) for m in data.get('results', []) if m.get('media_type') in ['movie', 'tv']]
    return jsonify(results[:20])

@app.route('/api/media/<media_type>/<int:tmdb_id>')
def media_details(media_type, tmdb_id):
    m = tmdb_get(f'/{media_type}/{tmdb_id}', {'append_to_response': 'credits,similar'})
    formatted = format_movie(m, media_type)
    formatted['runtime'] = m.get('runtime') or (m.get('episode_run_time', [0])[0] if m.get('episode_run_time') else 0)
    formatted['genres'] = [g['name'] for g in m.get('genres', [])]
    
    if media_type == 'tv':
        seasons = []
        for s in m.get('seasons', []):
            if s.get('season_number') > 0:
                seasons.append({
                    'season_number': s.get('season_number'),
                    'episode_count': s.get('episode_count'),
                    'name': s.get('name'),
                    'poster': f"https://image.tmdb.org/t/p/w500{s['poster_path']}" if s.get('poster_path') else formatted['poster']
                })
        formatted['seasons'] = seasons
    
    cast = []
    if 'credits' in m and 'cast' in m['credits']:
        for c in m['credits']['cast'][:10]:
            cast.append({
                'name': c.get('name', ''),
                'character': c.get('character', ''),
                'photo': f"https://image.tmdb.org/t/p/w185{c['profile_path']}" if c.get('profile_path') else ''
            })
    formatted['cast'] = cast
    
    similar = []
    if 'similar' in m and 'results' in m['similar']:
        similar = [format_movie(s, media_type) for s in m['similar']['results'][:10]]
    formatted['similar'] = similar
    
    return jsonify(formatted)

@app.route('/api/episodes/<int:tmdb_id>/<int:season_number>')
def tv_episodes(tmdb_id, season_number):
    data = tmdb_get(f'/tv/{tmdb_id}/season/{season_number}')
    episodes = []
    for e in data.get('episodes', []):
        episodes.append({
            'episode_number': e.get('episode_number'),
            'name': e.get('name'),
            'overview': e.get('overview'),
            'still': f"https://image.tmdb.org/t/p/w300{e['still_path']}" if e.get('still_path') else ''
        })
    return jsonify({'episodes': episodes})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
