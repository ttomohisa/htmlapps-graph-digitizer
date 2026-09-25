"""v0.8.3 UX regression: compact Results, explicit point editing, cohesive action groups."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]

async def click_pt(page,px,py):
    c=page.locator('#graphCanvas'); await c.scroll_into_view_if_needed(); box=await c.bounding_box(); assert box
    await page.mouse.click(box['x']+box['width']*px/900,box['y']+box['height']*py/540); await page.wait_for_timeout(40)

async def calibrate(page):
    for p in ((96,420),(770,420),(96,420),(96,85)): await click_pt(page,*p)

async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
    try:
      html=(R/'dist/index.html').read_text()
      page=await browser.new_page(viewport={'width':1440,'height':900},locale='ja-JP')
      errors=[]; network=[]
      page.on('pageerror',lambda e:errors.append(str(e)))
      page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None)
      await page.set_content(html,wait_until='load')
      assert await page.locator('#versionBadge').text_content()=='v1.0.0'
      await page.locator('#sampleButton').click(); await calibrate(page); await page.locator('#toExtractButton').click()
      # Manual point is added, selected, and the explicit repair CTA is enabled.
      await click_pt(page,430,285)
      assert await page.locator('#editSelectedPointButton').is_enabled()
      before=await page.locator('#selectedPointSummary').inner_text(); assert '手動' in before and 'px' in before
      await page.locator('#editSelectedPointButton').click(); assert await page.locator('#touchPrecision').is_visible()
      before_coord=await page.locator('#touchPrecisionCoords').text_content()
      await page.locator('[data-nudge="1,0"]').click(); await page.locator('#touchPrecisionApply').click()
      after=await page.locator('#selectedPointSummary').inner_text(); assert after!=before and '手動' in after
      assert not await page.locator('#touchPrecision').is_visible()
      # Results uses compact details and a capped desktop pane instead of one very tall left column.
      await page.locator('#toResultButton').click(); await page.wait_for_timeout(60)
      assert not await page.locator('#dataReviewDetails').get_attribute('open')
      assert not await page.locator('#csvPreviewDetails').get_attribute('open')
      metrics=await page.locator('.control-panel').evaluate("e=>({h:e.getBoundingClientRect().height,scroll:e.scrollHeight,cls:e.className})")
      assert 'is-results-mode' in metrics['cls'] and metrics['h'] <= 790, metrics
      # Editing from Results opens the same precise edit path instead of merely navigating away.
      await page.locator('#graphCanvas').click(position={'x':430/900*(await page.locator('#graphCanvas').bounding_box())['width'],'y':285/540*(await page.locator('#graphCanvas').bounding_box())['height']})
      if not await page.locator('#reviewEditButton').is_enabled():
          await page.locator('#dataReviewDetails').evaluate('e=>e.open=true')
          await page.locator('#pointRows tr').first.locator('button').click()
      await page.locator('#reviewEditButton').click(); assert await page.locator('#extractPage').is_visible(); assert await page.locator('#touchPrecision').is_visible()
      await page.locator('#touchPrecisionCancel').click()
      assert await page.locator('.control-group').count()>=4 and await page.locator('.button-cluster').count()>=5
      assert not errors,errors; assert not network,network
      print('PASS v0.8.3 UX: compact Results pane, grouped actions, explicit selected-point repair path',flush=True)
      await page.close()

      mobile=await browser.new_page(viewport={'width':320,'height':568},is_mobile=True,has_touch=True,locale='ja-JP')
      await mobile.set_content(html,wait_until='load'); await mobile.locator('#sampleButton').click(); await calibrate(mobile); await mobile.locator('[data-mobile-key="extract"]').click(); await click_pt(mobile,430,285)
      assert await mobile.locator('#editSelectedPointButton').is_visible(); assert await mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
      print('PASS v0.8.3 mobile 320x568 grouped controls have no horizontal overflow',flush=True)
      await mobile.close()
    finally:
      await browser.close()

asyncio.run(main())
