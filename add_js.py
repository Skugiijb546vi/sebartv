with open('templates/index.html', 'r', encoding='utf-8') as f: text = f.read()

missing_js = '''
async function search() {
  const q = document.getElementById('searchInput').value.trim();
  if (!q) return;
  document.getElementById('searchSection').style.display = 'block';
  document.querySelector('.hero').style.display = 'none';
  const searchResults = document.getElementById('searchResults');
  searchResults.innerHTML = '<div style="padding:40px;text-align:center;">Searching...</div>';
  try {
    const data = await fetch(`/api/search?q=${encodeURIComponent(q)}`).then(r => r.json());
    if (data.length) {
      searchResults.innerHTML = data.map(m => cardHTML(m)).join('');
    } else {
      searchResults.innerHTML = '<div style="padding:40px;text-align:center;">No results found</div>';
    }
  } catch (err) {
    searchResults.innerHTML = '<div style="padding:40px;text-align:center;">Error searching</div>';
  }
}

document.getElementById('searchInput').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') search();
});

async function init() {
  try {
    const trendingData = await fetch('/api/trending').then(r => r.json());
    document.getElementById('trendingRow').innerHTML = trendingData.map(m => cardHTML(m)).join('');
    
    const animeData = await fetch('/api/anime').then(r => r.json());
    document.getElementById('animeRow').innerHTML = animeData.map(m => cardHTML(m)).join('');
    
    const dramaData = await fetch('/api/drama').then(r => r.json());
    document.getElementById('dramaRow').innerHTML = dramaData.map(m => cardHTML(m)).join('');
    
    const genres = await fetch('/api/genres').then(r => r.json());
    const bar = document.getElementById('genreBar');
    bar.innerHTML = genres.slice(0, 12).map(g => `<button class="genre-chip" onclick="viewGenre(${g.id}, '${g.name}')">${g.name}</button>`).join('');
  } catch (err) {
    console.error('Error loading data:', err);
  }
}

async function viewGenre(id, name) {
  document.querySelector('.hero').style.display = 'none';
  document.getElementById('searchSection').style.display = 'none';
  document.getElementById('genreSection').style.display = 'block';
  document.getElementById('genreTitle').textContent = name + ' Movies';
  const genreRow = document.getElementById('genreRow');
  genreRow.innerHTML = '<div style="padding:40px;text-align:center;">Loading...</div>';
  
  try {
    const data = await fetch(`/api/genre/${id}`).then(r => r.json());
    genreRow.innerHTML = data.map(m => cardHTML(m)).join('');
  } catch (err) {
    genreRow.innerHTML = '<div style="padding:40px;text-align:center;">Error loading genre</div>';
  }
}

init();
</script>'''

text = text.replace('</script>', missing_js + '\n</script>')
# We need to make sure we don't have multiple </script> tags.
text = text.replace('</script>\n</script>', '</script>')

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Added missing JS back')
