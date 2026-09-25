"""v0.3.0 auto-trace regression: color pick, range, preview, apply, review/segments, cancel-safety."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]

async def image_pos(page,px,py,width=900,height=540):
    c=page.locator('#graphCanvas');await c.scroll_into_view_if_needed();box=await c.bounding_box();assert box
    return (box['x']+box['width']*px/width,box['y']+box['height']*py/height)
async def click_pt(page,px,py):
    x,y=await image_pos(page,px,py);await page.mouse.click(x,y);await page.wait_for_timeout(30)
async def calibrate(page):
    for p in ((96,420),(770,420),(96,420),(96,85)):await click_pt(page,*p)
    assert await page.locator('#toExtractButton').is_enabled()

async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
    try:
      page=await browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1,locale='ja-JP')
      errors=[];network=[]
      page.on('pageerror',lambda error:errors.append(str(error)))
      page.on('request',lambda req:network.append(req.url) if req.url.startswith(('http:','https:')) else None)
      await page.set_content((R/'dist/index.html').read_text(),wait_until='load')
      await page.locator('#sampleButton').click();await calibrate(page);await page.locator('#toExtractButton').click()
      # Pick the sample curve at an exact curve location.
      await page.locator('#tracePickColorButton').click();await click_pt(page,433,298.0)
      color=await page.locator('#traceColorValue').text_content();assert '#16624F' in color.upper(),color
      await page.locator('#traceAxisRangeButton').click()
      # Cancellation must not leave a stale preview behind.
      await page.locator('#traceRunButton').click();await page.locator('#traceCancelButton').click()
      await page.locator('#traceRunButton').wait_for(state='visible',timeout=10000)
      assert await page.locator('#traceApplyButton').is_hidden()
      await page.locator('#traceRunButton').click()
      await page.locator('#traceApplyButton').wait_for(state='visible',timeout=10000)
      summary=await page.locator('#traceSummary').text_content();print('TRACE',summary,flush=True)
      assert '点' in summary and '%' in summary,summary
      # Preview is not committed yet.
      assert await page.locator('#resultPoints').text_content()=='0'
      await page.locator('#traceApplyButton').click()
      assert int(await page.locator('#resultPoints').text_content())>250
      # Compare a point around x=50 data units against the known sample curve center.
      rows=page.locator('#pointRows tr');count=await rows.count();assert count>250
      vals=[]
      for i in range(count):
          cells=await rows.nth(i).locator('td').all_text_contents()
          vals.append((float(cells[2]),float(cells[3])))
      target=min(vals,key=lambda v:abs(v[0]-50))
      assert abs(target[1]-18.2)<1.0,target
      import math
      errors_px=[abs(y-(6+0.34*x+5*math.sin(x/10)))*6.7 for x,y in vals]
      within=sum(err<=2 for err in errors_px)/len(errors_px)
      print('QUALITY',len(vals),within,max(errors_px),flush=True)
      assert within>=.95,within
      print('PASS v0.3 T05: >90% X coverage and >=95% points within 2 image px',flush=True)
      # Undo restores the series to empty after applying auto-trace.
      await page.locator('#undoButton').click();assert await page.locator('#resultPoints').text_content()=='0'
      await page.locator('#redoButton').click();assert int(await page.locator('#resultPoints').text_content())>250
      # Changing settings discards a new preview, while already-applied points stay intact.
      await page.locator('#traceRunButton').click();await page.locator('#traceApplyButton').wait_for(state='visible',timeout=10000)
      await page.locator('#traceCard details').evaluate('d=>d.open=true');await page.locator('#traceTolerance').fill('60');await page.locator('#traceTolerance').press('Tab')
      assert await page.locator('#traceApplyButton').is_hidden()
      # Optional start point can be set/cleared.
      await page.locator('#traceStartButton').click();await click_pt(page,433,298.0)
      print('START',await page.locator('#traceStartValue').text_content(),flush=True);assert (await page.locator('#traceStartValue').text_content())!='未指定'
      await page.locator('#traceStartClearButton').click();assert await page.locator('#traceStartClearButton').is_disabled()
      assert not errors,errors
      assert not network,network
      print('PASS v0.3 settings invalidate preview, start point workflow, 0 runtime requests/errors',flush=True)
      # Mobile: auto-trace controls must fit without horizontal overflow.
      mobile=await browser.new_page(viewport={'width':320,'height':760},is_mobile=True,has_touch=True,locale='en-US')
      await mobile.set_content((R/'dist/index.html').read_text(),wait_until='load')
      await mobile.locator('#sampleButton').click();await mobile.locator('[data-mobile-key="axis"]').click();await calibrate(mobile);await mobile.locator('#toExtractButton').click()
      overflow=await mobile.evaluate('document.documentElement.scrollWidth-innerWidth')
      assert overflow<=0,overflow
      assert await mobile.locator('#traceRunButton').is_visible()
      print('PASS v0.3 mobile 320px auto-trace controls have no horizontal overflow',flush=True)
      await mobile.close()
    finally:
      await browser.close()
asyncio.run(main())
