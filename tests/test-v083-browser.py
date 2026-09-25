"""v0.8.3 UI regression: header copy, aligned review badge, cohesive auto-trace controls."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]

async def click_pt(page,px,py):
    c=page.locator('#graphCanvas'); await c.scroll_into_view_if_needed(); box=await c.bounding_box(); assert box
    await page.mouse.click(box['x']+box['width']*px/900,box['y']+box['height']*py/540); await page.wait_for_timeout(30)

async def calibrate(page):
    for p in ((96,420),(770,420),(96,420),(96,85)): await click_pt(page,*p)

async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
    try:
      html=(R/'dist/index.html').read_text()
      page=await browser.new_page(viewport={'width':1280,'height':900},locale='ja-JP')
      errors=[]; network=[]
      page.on('pageerror',lambda e:errors.append(str(e)))
      page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None)
      await page.set_content(html,wait_until='load')
      assert await page.locator('#versionBadge').text_content()=='v1.0.0'
      meta=(await page.locator('.brand-meta').text_content()).strip()
      assert '完全ローカル処理' not in meta and '自動追跡' in meta
      assert (await page.locator('.local-badge').inner_text()).strip()=='完全ローカル処理'
      await page.locator('#sampleButton').click(); await calibrate(page); await page.locator('#toExtractButton').click()
      # Auto-trace settings are three consistent rows and range choice is segmented/pressed.
      assert await page.locator('#traceCard .trace-setting').count()>=3
      await page.locator('#traceAxisRangeButton').click(); await page.wait_for_timeout(40)
      assert await page.locator('#traceAxisRangeButton').get_attribute('aria-pressed')=='true'
      assert await page.locator('#traceRangeButton').get_attribute('aria-pressed')=='false'
      # Generate preview and ensure Run is replaced by Apply/Discard rather than all three actions at once.
      await page.locator('#tracePickColorButton').click(); await click_pt(page,430,285)
      await page.locator('#traceRunButton').click(); await page.wait_for_timeout(450)
      assert await page.locator('#traceRunButton').is_hidden()
      assert await page.locator('#traceApplyButton').is_visible() and await page.locator('#traceDiscardButton').is_visible()
      await page.locator('#traceApplyButton').click(); await page.locator('#toResultButton').click(); await page.wait_for_timeout(50)
      # Clear badge shares the title baseline and stays vertically centered.
      title=await page.locator('#reviewTitle').bounding_box(); badge=await page.locator('#reviewBadge').bounding_box(); assert title and badge
      assert abs((title['y']+title['height']/2)-(badge['y']+badge['height']/2)) <= 4, (title,badge)
      assert not errors,errors; assert not network,network
      print('PASS v0.8.3 UI: product header copy, aligned review badge, cohesive auto-trace flow',flush=True)
      await page.close()
      mobile=await browser.new_page(viewport={'width':320,'height':568},is_mobile=True,has_touch=True,locale='ja-JP')
      await mobile.set_content(html,wait_until='load'); await mobile.locator('#sampleButton').click(); await calibrate(mobile); await mobile.locator('[data-mobile-key="extract"]').click()
      assert await mobile.locator('#traceCard .trace-setting').count()>=3
      assert await mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
      print('PASS v0.8.3 mobile auto-trace settings have no horizontal overflow',flush=True)
      await mobile.close()
    finally:
      await browser.close()

asyncio.run(main())
