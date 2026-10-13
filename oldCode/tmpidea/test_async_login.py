import asyncio
from playwright.async_api import async_playwright

async def test():
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=False)
    ctx = await browser.new_context(viewport={"width":1440,"height":900}, ignore_https_errors=True)
    page = await ctx.new_page()
    await page.goto("http://172.16.1.165:9100/adminLogin")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(3000)

    await page.locator('input[placeholder="账号"]').fill("17695729351")
    await page.locator('input[type="password"]').fill("123456")

    user_val = await page.locator('input[placeholder="账号"]').input_value()
    print(f"async user value: {user_val}")

    await page.locator('button:has-text("登 录")').click(force=True)
    await page.wait_for_timeout(5000)
    print(f"async url after login: {page.url}")

    await browser.close()
    await pw.stop()

asyncio.run(test())
