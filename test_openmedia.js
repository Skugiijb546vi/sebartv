function openMedia(tmdbId, mediaType) {
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
      document.getElementById('playerStatus').textContent = '❌ ئەم فیلمە هێشتا بڵاونەکراوەتەوە یان لە سێرڤەرەکانمان بەردەست نییە. تکایە فیلمێکی تر تاقی بکەرەوە.';
      document.getElementById('playerStatus').className = 'player-error';
    }
  } catch (err)