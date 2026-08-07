from playwright.sync_api import sync_playwright

def test_extractor(url):
    m3u8_url = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        def handle_response(response):
            nonlocal m3u8_url
            if '.m3u8' in response.url and 'master' not in response.url.lower():
                print('Found m3u8:', response.url)
                if not m3u8_url:
                    m3u8_url = response.url
                    
        page.on("response", handle_response)
        
        print(f'Navigating to {url}...')
        page.goto(url)
        page.wait_for_timeout(8000) # wait 8 seconds for JS to load the stream
        browser.close()
    return m3u8_url

if __name__ == "__main__":
    test_extractor("https://vidlink.pro/movie/1368337")
    test_extractor("https://autoembed.co/movie/tmdb/1368337")
