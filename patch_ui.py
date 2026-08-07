import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('<h2 class="section-title">🔥 Trending Now</h2>', '<div style="display:flex; justify-content:space-between; align-items:center; padding-right:14px;"><h2 class="section-title" style="margin-bottom:0;">🔥 Trending Now</h2><button onclick="viewAll(\'Trending\')" class="genre-chip">Bînînî Hemû</button></div>')
html = html.replace('<h2 class="section-title">✨ Anime</h2>', '<div style="display:flex; justify-content:space-between; align-items:center; padding-right:14px;"><h2 class="section-title" style="margin-bottom:0;">✨ Anime</h2><button onclick="viewAll(\'Anime\')" class="genre-chip">Bînînî Hemû</button></div>')
html = html.replace('<h2 class="section-title">🎭 Drama</h2>', '<div style="display:flex; justify-content:space-between; align-items:center; padding-right:14px;"><h2 class="section-title" style="margin-bottom:0;">🎭 Drama</h2><button onclick="viewAll(\'Drama\')" class="genre-chip">Bînînî Hemû</button></div>')

view_all_script = """
let cachedData = { Trending: [], Anime: [], Drama: [] };

async function viewAll(category) {
  const section = document.getElementById('genreSection');
  document.getElementById('genreSectionTitle').textContent = `🎬 Hemû ` + category;
  document.getElementById('genreRow').style.flexWrap = 'wrap';
  document.getElementById('genreRow').innerHTML = cachedData[category].map(m => cardHTML(m)).join('');
  section.style.display = 'block';
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
"""

if 'let cachedData' not in html:
    html = html.replace('let searchTimeout = null;', 'let searchTimeout = null;\n' + view_all_script)
    html = html.replace("document.getElementById('trendingRow').innerHTML = trendingData.map(m => cardHTML(m)).join('');", "cachedData.Trending = trendingData;\ndocument.getElementById('trendingRow').innerHTML = trendingData.map(m => cardHTML(m)).join('');")
    html = html.replace("document.getElementById('animeRow').innerHTML = animeData.map(m => cardHTML(m)).join('');", "cachedData.Anime = animeData;\ndocument.getElementById('animeRow').innerHTML = animeData.map(m => cardHTML(m)).join('');")
    html = html.replace("document.getElementById('dramaRow').innerHTML = dramaData.map(m => cardHTML(m)).join('');", "cachedData.Drama = dramaData;\ndocument.getElementById('dramaRow').innerHTML = dramaData.map(m => cardHTML(m)).join('');")
    html = html.replace("document.getElementById('genreRow').innerHTML = data.map(m => cardHTML(m)).join('');", "document.getElementById('genreRow').style.flexWrap = 'nowrap';\ndocument.getElementById('genreRow').innerHTML = data.map(m => cardHTML(m)).join('');")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
