import asyncio
from playwright.async_api import async_playwright

async def extract_tv_stream(tmdb_id, season=1, episode=1):
    url = f"https://vidsrc.hair/embed/tv/{tmdb_id}/{season}/{episode}"
    m3u8_url = None

    async def handle_request(request):
        nonlocal m3u8_url
        if '.m3u8' in request.url:
            m3u8_url = request.url

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.on("request", handle_request)
        
        try:
            print(f'Navigating to {url}')
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            
            # Wait a few seconds for cloudflare and the video player to load
            for _ in range(10):
                if m3u8_url:
                    break
                await page.wait_for_timeout(1000)
                
        except Exception as e:
            print('Error during navigation:', e)
            
        await browser.close()
        
    return m3u8_url

if __name__ == '__main__':
    res = asyncio.run(extract_tv_stream('95479'))
    print('Final Stream:', res)
