with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add iframe-player right before main-video if not already there
if 'id="iframe-player"' not in html:
    html = html.replace('<video id="main-video"', '<iframe id="iframe-player" style="display:none;width:100%;height:100%;border:none;" allowfullscreen></iframe>\n        <video id="main-video"')

# 2. Update startHLS
old_hls = 'function startHLS(url, type) {'
new_hls = '''function startHLS(url, type) {
  const video = document.getElementById('main-video');
  const iframe = document.getElementById('iframe-player');
  
  if (type === 'iframe') {
    video.style.display = 'none';
    if (iframe) {
        iframe.style.display = 'block';
        iframe.src = url;
    }
    if (currentHls) { currentHls.destroy(); currentHls = null; }
    return;
  }
  
  if (iframe) iframe.style.display = 'none';
  video.style.display = 'block';'''

if "if (type === 'iframe')" not in html:
    html = html.replace(old_hls, new_hls)

# 3. Update stopPlayer
old_stop = 'function stopPlayer() {'
new_stop = '''function stopPlayer() {
  const iframe = document.getElementById('iframe-player');
  if (iframe) iframe.src = '';'''

if 'iframe.src =' not in html.split('function stopPlayer() {')[1][:100]:
    html = html.replace(old_stop, new_stop)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
