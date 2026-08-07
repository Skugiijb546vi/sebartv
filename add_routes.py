with open('app.py', 'r', encoding='utf-8') as f: lines = f.readlines()

missing_routes = '''
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
    m = tmdb_get(f'/{media_type}/{tmdb_id}')
    return jsonify(format_movie(m, media_type))
'''

# Find where to insert (before if __name__ == '__main__':)
insert_idx = len(lines)
for i, line in enumerate(lines):
    if "if __name__ == '__main__':" in line:
        insert_idx = i - 1
        break

lines.insert(insert_idx, missing_routes)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Routes added.")
