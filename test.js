
// ─── State ────────────────────────────────────────────────────────────────
let currentHls = null;
let heroMovie = null;
let searchTimeout = null;

let cachedData = { Trending: [], Anime: [], Drama: [] };

async function viewAll(category) {
  const section = document.getElementById('genreSection');
  document.getElementById('genreSectionTitle').textContent = `🎬 Hemû ` + category;
  document.getElementById('genreRow').style.flexWrap = 'wrap';
  document.getElementById('genreRow').innerHTML = cachedData[category].map(m => cardHTML(m)).join('');
  section.style.display = 'block';
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}


// ─── Nav scroll effect ──────────────────────────────────────────────────
window.addEventListener('scroll', () => {
  document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 50);
});

// ─── Search ─────────────────────────────────────────────────────────────
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');

searchInput.addEventListener('input', (e) => {
  clearTimeout(searchTimeout);
  const q = e.target.value.trim();
  if (q.length < 2) { searchResults.classList.remove('active'); return; }
  searchTimeout = setTimeout(() => {
    fetch(`/api/search?q=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .then(data => {
        if (!data.length) { searchResults.classList.remove('active'); return; }
        searchResults.innerHTML = data.map(m => `
          <div class="search-item" onclick="openMedia(${m.id}, '${m.media_type || 'movie'}')">
            <img src="${m.poster || 'https://placehold.co/40x60/1a1a28/555.png?text=N/A'}" alt="" loading="eager">
            <div class="search-item-info">
              <h4>${m.title}</h4>
              <span>⭐ ${m.rating?.toFixed(1) || 'N/A'} · ${m.year || ''}</span>
            </div>
          </div>
        `).join('');
        searchResults.classList.add('active');
      });
  }, 300);
});

document.addEventListener('click', (e) => {
  if (!e.target.closest('.search-box')) searchResults.classList.remove('active');
});

// ─── Load Content ──────────────────────────────────────────────────────
async function loadContent() {
  // Trending
  const trendingData = await fetch('/api/trending').then(r => r.json());
  if (trendingData.length) {
    heroMovie = trendingData[0];
    const heroBg = document.getElementById('heroBg');
    heroBg.style.backgroundImage = `url(${heroMovie.backdrop})`;
    document.getElementById('heroContent').innerHTML = `
      <div class="hero-meta">
        <span class="rating">⭐ ${heroMovie.rating?.toFixed(1)}</span>
        <span>${heroMovie.year}</span>
      </div>
      <h1>${heroMovie.title}</h1>
      <p>${heroMovie.overview}</p>
      <div class="hero-btns">
        <button class="btn-play" onclick="playMedia(${heroMovie.id}, '${heroMovie.media_type || 'movie'}')">▶ Play</button>
        <button class="btn-info" onclick="openMedia(${heroMovie.id}, '${heroMovie.media_type || 'movie'}')">ℹ More Info</button>
      </div>
    `;
    cachedData.Trending = trendingData;
document.getElementById('trendingRow').innerHTML = trendingData.map(m => cardHTML(m)).join('');
  }

  // Anime
  const animeData = await fetch('/api/anime').then(r => r.json());
  cachedData.Anime = animeData;
document.getElementById('animeRow').innerHTML = animeData.map(m => cardHTML(m)).join('');

  // Drama
  const dramaData = await fetch('/api/drama').then(r => r.json());
  cachedData.Drama = dramaData;
document.getElementById('dramaRow').innerHTML = dramaData.map(m => cardHTML(m)).join('');
}

// ─── Load Genres ────────────────────────────────────────────────────────
async function loadGenres() {
  const genres = await fetch('/api/genres').then(r => r.json());
  const bar = document.getElementById('genreBar');
  bar.innerHTML = genres.slice(0, 12).map(g =>
    `<button class="genre-chip" onclick="loadGenre(${g.id}, '${g.name}', this)">${g.name}</button>`
  ).join('');
}

async function loadGenre(id, name, btn) {
  document.querySelectorAll('.genre-chip').forEach(c => c.classList.remove('active'));
  if (btn) btn.classList.add('active');

  const data = await fetch(`/api/genre/${id}`).then(r => r.json());
  const section = document.getElementById('genreSection');
  document.getElementById('genreSectionTitle').textContent = `🎬 ${name}`;
  document.getElementById('genreRow').style.flexWrap = 'nowrap';
document.getElementById('genreRow').innerHTML = data.map(m => cardHTML(m)).join('');
  section.style.display = 'block';
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ─── Card HTML ──────────────────────────────────────────────────────────
function cardHTML(m) {
  return `
    <div class="card" onclick="openMedia(${m.id}, '${m.media_type || 'movie'}')">
      <img src="${m.poster || 'https://placehold.co/180x270/1a1a28/555.png?text=N/A'}" alt="${m.title}" loading="eager">
      <span class="card-rating">⭐ ${m.rating?.toFixed(1) || ''}</span>
      <div class="card-overlay">
        <h4>${m.title}</h4>
        <span>${m.year || ''}</span>
      </div>
    </div>
  `;
}

// ─── Movie Modal ────────────────────────────────────────────────────────
async function openMedia(tmdbId, mediaType) {
  searchResults.classList.remove('active');
  searchInput.value = '';

  const m = await fetch(`/api/media/${mediaType}/${tmdbId}`).then(r => r.json());

  // Reset player
  stopPlayer();
  document.getElementById('playerWrap').style.display = 'none';

  const body = document.getElementById('modalBody');
  body.innerHTML = `
    <h2>${m.title}</h2>
    <div class="modal-meta">
      <span class="rating">⭐ ${m.rating?.toFixed(1)}</span>
      <span>${m.year}</span>
      ${m.runtime ? `<span>${m.runtime} min</span>` : ''}
    </div>
    <div class="modal-genres">
      ${m.genres.map(g => `<span>${g}</span>`).join('')}
    </div>
    <div style="margin-bottom:20px;">
      <button class="btn-play" onclick="playMedia(${m.id}, '${mediaType}')">▶ Play</button>
    </div>
    <p class="overview">${m.overview}</p>
    ${m.cast.length ? `
      <h3 style="font-size:16px;margin-bottom:12px;font-weight:700;">Cast</h3>
      <div class="cast-row">
        ${m.cast.map(c => `
          <div class="cast-item">
            <img src="${c.photo || 'https://placehold.co/64x64/1a1a28/555.png?text=?'}" alt="${c.name}" loading="eager">
            <div class="cast-name">${c.name}</div>
            <div class="cast-char">${c.character}</div>
          </div>
        `).join('')}
      </div>
    ` : ''}
    ${m.similar.length ? `
      <h3 style="font-size:16px;margin-bottom:12px;font-weight:700;">Similar</h3>
      <div class="row">
        ${m.similar.map(s => cardHTML(s)).join('')}
      </div>
    ` : ''}
  `;

  const overlay = document.getElementById('modalOverlay');
  overlay.classList.add('active');
}

function closeModal() {
  stopPlayer();
  document.getElementById('modalOverlay').classList.remove('active');
}

document.getElementById('modalOverlay').addEventListener('click', (e) => {
  if (e.target === document.getElementById('modalOverlay')) closeModal();
});

// ─── Player ─────────────────────────────────────────────────────────────
async function playMedia(tmdbId, mediaType) {
  const playerWrap = document.getElementById('playerWrap');
  playerWrap.style.display = 'block';
  document.getElementById('playerLoading').style.display = 'flex';
  document.getElementById('playerStatus').textContent = 'Extracting stream...';
  document.getElementById('playerStatus').className = '';
  document.getElementById('modalOverlay').classList.add('active');
  playerWrap.scrollIntoView({ behavior: 'smooth' });

  try {
    const resp = await fetch(`/api/play/${mediaType}/${tmdbId}`);
    const data = await resp.json();
    
    if (data.success) {
      document.getElementById('playerStatus').textContent = 'Stream found!';
      document.getElementById('playerLoading').style.display = 'none';
      const playerContainer = document.getElementById('playerContainer');
      if (data.stream_type === 'iframe') {
        playerContainer.innerHTML = `<iframe src="${data.stream_url}" sandbox="allow-scripts allow-same-origin" allowfullscreen style="width: 100%; height: 100%; border: none; overflow: hidden;" scrolling="no"></iframe>`;
      } else {
        const video = document.createElement('video');
        video.id = 'video-player';
        video.controls = true;
        video.autoplay = true;
        playerContainer.innerHTML = '';
        playerContainer.appendChild(video);
        if (Hls.isSupported() && data.stream_url.includes('.m3u8')) {
          const hls = new Hls();
          hls.loadSource(data.stream_url);
          hls.attachMedia(video);
        } else {
          video.src = data.stream_url;
        }
      }
    } else {
      document.getElementById('playerStatus').textContent = 'This movie is not available on our servers yet.';
      document.getElementById('playerStatus').className = 'player-error';
    }
  } catch (err) {
    document.getElementById('playerStatus').textContent = 'Failed to load stream.';
    document.getElementById('playerStatus').className = 'player-error';
  }
}

function stopPlayer() {
  const playerContainer = document.getElementById('playerContainer');
  playerContainer.innerHTML = '';
  document.getElementById('playerWrap').style.display = 'none';
}

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
