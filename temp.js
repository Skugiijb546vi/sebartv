
// ─── State ────────────────────────────────────────────────────────────────
let currentHls = null;
let heroMovie = null;
let searchTimeout = null;

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
            <img src="${m.poster || 'https://via.placeholder.com/40x60/1a1a28/555?text=N/A'}" alt="">
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
    document.getElementById('trendingRow').innerHTML = trendingData.map(m => cardHTML(m)).join('');
  }

  // Anime
  const animeData = await fetch('/api/anime').then(r => r.json());
  document.getElementById('animeRow').innerHTML = animeData.map(m => cardHTML(m)).join('');

  // Drama
  const dramaData = await fetch('/api/drama').then(r => r.json());
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
  document.getElementById('genreRow').innerHTML = data.map(m => cardHTML(m)).join('');
  section.style.display = 'block';
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ─── Card HTML ──────────────────────────────────────────────────────────
function cardHTML(m) {
  return `
    <div class="card" onclick="openMedia(${m.id}, '${m.media_type || 'movie'}')">
      <img src="${m.poster || 'https://via.placeholder.com/180x270/1a1a28/555?text=N/A'}" alt="${m.title}" loading="lazy">
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
            <img src="${c.photo || 'https://via.placeholder.com/64/1a1a28/555?text=?'}" alt="${c.name}">
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
  // Show player
  const playerWrap = document.getElementById('playerWrap');
  playerWrap.style.display = 'block';
  document.getElementById('playerLoading').style.display = 'flex';
  document.getElementById('playerStatus').textContent = 'Extracting stream...';
  document.getElementById('playerStatus').className = '';

  // Make sure modal is open
  document.getElementById('modalOverlay').classList.add('active');

  // Scroll player into view
  playerWrap.scrollIntoView({ behavior: 'smooth' });

  try {
    const resp = await fetch(`/api/play/${mediaType}/${tmdbId}`);
    const data = await resp.json();

    if (data.success && data.stream_url) {
      document.getElementById('playerStatus').textContent = `Stream found! (${data.server_count} servers available)`;
      setTimeout(() => startHLS(data.stream_url, data.stream_type), 500);
    } else {
      document.getElementById('playerStatus').textContent = '❌ ' + (data.error || 'Stream not available');
      document.getElementById('playerStatus').className = 'player-error';
    }
  } catch (err) {
    document.getElementById('playerStatus').textContent = '❌ Connection error';
    document.getElementById('playerStatus').className = 'player-error';
  }
}

function startHLS(url, type) {
  stopPlayer();
  const video = document.getElementById('videoPlayer');

  if (type === 'mp4') {
    video.src = url;
    video.play().catch(() => {});
    document.getElementById('playerLoading').style.display = 'none';
    return;
  }

  if (Hls.isSupported()) {
    currentHls = new Hls({ maxBufferLength: 30 });
    currentHls.loadSource(url);
    currentHls.attachMedia(video);
    currentHls.on(Hls.Events.MANIFEST_PARSED, () => {
      document.getElementById('playerLoading').style.display = 'none';
      video.play().catch(() => {});
    });
    currentHls.on(Hls.Events.ERROR, (_, data) => {
      if (data.fatal) {
        document.getElementById('playerStatus').textContent = '❌ Stream playback error';
        document.getElementById('playerStatus').className = 'player-error';
      }
    });
  } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = url;
    video.addEventListener('loadedmetadata', () => {
      document.getElementById('playerLoading').style.display = 'none';
      video.play().catch(() => {});
    });
  }
}

function stopPlayer() {
  const video = document.getElementById('videoPlayer');
  if (currentHls) { currentHls.destroy(); currentHls = null; }
  video.pause();
  video.removeAttribute('src');
  video.load();
}

// ─── Keyboard ───────────────────────────────────────────────────────────
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});

// ─── Init ───────────────────────────────────────────────────────────────
loadContent();
loadGenres();
