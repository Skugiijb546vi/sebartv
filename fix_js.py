import sys
import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix openMedia to be async
text = text.replace('function openMedia(tmdbId, mediaType)', 'async function openMedia(tmdbId, mediaType)')

correct_playMedia = '''async function playMedia(tmdbId, mediaType) {
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
</script>'''

# Replace everything from async function playMedia or function playMedia to </script>
text = re.sub(r'(async )?function playMedia\(tmdbId, mediaType\).*?</script>', correct_playMedia, text, flags=re.DOTALL)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed JS')
