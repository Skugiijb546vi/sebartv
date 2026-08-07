import re
with open('templates/index.html', 'r', encoding='utf-8') as f: text = f.read()

new_logic = '''const resp = await fetch(`/api/play/${mediaType}/${tmdbId}`);
    const data = await resp.json();
    
    if (data.success) {
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
    } else if (data.success === false)'''

text = re.sub(r'const resp = await fetch.*?.api/play.*?;.*?if \(data\.success\) \{.*?else if \(data\.success === false\)', new_logic, text, flags=re.DOTALL)
with open('templates/index.html', 'w', encoding='utf-8') as f: f.write(text)
print('Updated index.html')
