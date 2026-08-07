import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        async def handle_request(request):
            if '.m3u8' in request.url:
                print('Found m3u8:', request.url)

        page.on("request", handle_request)
        
        try:
            print('Navigating to vidsrc.cc...')
            await page.goto('https://vidsrc.cc/v2/embed/tv/95479/1/1', wait_until='networkidle')
            await page.wait_for_timeout(10000)
            
            # vidsrc.cc has a big play button. Let's try to click it if it exists.
            content = await page.content()
            if '<button' in content or 'play' in content.lower():
                try:
                    await page.mouse.click(500, 500)
                    await page.wait_for_timeout(5000)
                except:
                    pass
        except Exception as e:
            print('Error:', e)
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
