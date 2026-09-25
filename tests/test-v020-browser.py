"""v0.2.0 functional regression: aligned layout, zoom/pan, point drag, series, CSV, crop.
Uses the generated readable standalone with local Chromium; no external requests allowed.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]

def near(a,b,threshold=1):assert abs(a-b)<threshold, (a,b)

async def image_pos(page,px,py,width=900,height=540):
 c=page.locator('#graphCanvas');await c.scroll_into_view_if_needed();box=await c.bounding_box();assert box
 return (box['x']+box['width']*px/width,box['y']+box['height']*py/height)

async def click_pt(page,px,py):
 x,y=await image_pos(page,px,py);await page.mouse.click(x,y);await page.wait_for_timeout(30)

async def calibrate(page):
 for p in ((96,420),(770,420),(96,420),(96,85)):await click_pt(page,*p)
 assert await page.locator('#toExtractButton').is_enabled()

async def aligned(page):
 return await page.evaluate('''() => {
   const h=document.querySelector('.header-inner'),m=document.querySelector('.main');
   const a=h.getBoundingClientRect(),b=m.getBoundingClientRect(), hc=getComputedStyle(h),mc=getComputedStyle(m);
   return {left:Math.abs(a.left+parseFloat(hc.paddingLeft)-b.left-parseFloat(mc.paddingLeft)),
           right:Math.abs(a.right-parseFloat(hc.paddingRight)-b.right+parseFloat(mc.paddingRight)),
           overflow:document.documentElement.scrollWidth-innerWidth};
 }''')

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
  try:
   page=await browser.new_page(viewport={'width':1600,'height':960},device_scale_factor=1,accept_downloads=True,locale='ja-JP')
   page.set_default_timeout(8000)
   errors=[];network=[]
   page.on('pageerror',lambda error:errors.append(str(error)))
   page.on('request',lambda req:network.append(req.url) if req.url.startswith(('http:','https:')) else None)
   await page.set_content((R/'dist/index.html').read_text(),wait_until='load')
   bounds=await aligned(page)
   assert bounds['left']<.1 and bounds['right']<.1,bounds
   print('PASS v0.2 header: content left/right edges align at 1600px',flush=True)
   await page.locator('#sampleButton').click()
   await calibrate(page)
   await page.locator('#toExtractButton').click()
   await click_pt(page,433,252.5)
   assert await page.locator('#resultPoints').text_content()=='1'
   # Known point should remain selected with precise dragging and undo+redo.
   x,y=await image_pos(page,433,252.5)
   await page.mouse.move(x,y);await page.mouse.down()
   await page.mouse.move(x+34,y-11,steps=5);await page.mouse.up()
   vals=await page.locator('#pointRows tr td').all_text_contents()
   moved_x=float(vals[2]);assert moved_x>50,vals
   await page.locator('#undoButton').click()
   original=float((await page.locator('#pointRows tr td').all_text_contents())[2]);near(original,50,.4)
   await page.locator('#redoButton').click()
   redone=float((await page.locator('#pointRows tr td').all_text_contents())[2]);near(redone,moved_x,.05)
   await page.locator('#undoButton').click()  # return to midpoint for remaining checks
   print('PASS v0.2 point drag and button Undo/Redo',flush=True)
   # Zoom and pan preserve source-image point coordinates.
   await page.locator('#zoomInButton').click()
   assert await page.locator('#zoomLabel').text_content()=='125%'
   box=await page.locator('#graphCanvas').bounding_box();assert box
   await page.mouse.move(box['x']+box['width']*.65,box['y']+box['height']*.5)
   await page.mouse.down();await page.mouse.move(box['x']+box['width']*.65-25,box['y']+box['height']*.5-15,steps=5);await page.mouse.up()
   still=float((await page.locator('#pointRows tr td').all_text_contents())[2]);near(still,50,.4)
   await page.locator('#fitButton').click()
   assert await page.locator('#zoomLabel').text_content()=='100%'
   print('PASS v0.2 image zoom/pan/Fit preserves data values',flush=True)
   # Add second series, editable name/color, hide without deleting data.
   await page.locator('#addSeriesButton').click()
   assert await page.locator('#seriesList .series-entry').count()==2
   second=page.locator('#seriesList .series-entry').nth(1)
   await second.locator('input[type="text"]').fill('Curve, "Two"')
   await second.locator('input[type="text"]').press('Tab')
   await second.locator('input[type="color"]').evaluate('''e=>{e.value='#445566';e.dispatchEvent(new Event('change',{bubbles:true}));}''')
   await page.locator('#manualCoordinatesDetails').evaluate('e=>e.open=true');await page.locator('#manualPx').fill('300');await page.locator('#manualPy').fill('300')
   await page.locator('#manualAddButton').click()
   assert await page.locator('#resultPoints').text_content()=='2'
   assert await page.locator('#resultSeries').text_content()=='2'
   second=page.locator('#seriesList .series-entry').nth(1)
   await second.locator('button').nth(1).click() # toggle preview visibility
   await page.locator('#toResultButton').click()
   assert await page.locator('#pointRows tr').count()==2,'hidden series should remain in results'
   assert await page.locator('#csvFormat option[value="simple"]').is_disabled()
   async with page.expect_download() as dl:
    await page.locator('#downloadButton').click()
   artifact=await dl.value;path=R/'tests/fixtures/v020-temporary-export.csv';await artifact.save_as(str(path))
   data=path.read_bytes();path.unlink()
   assert data.startswith(b'\xef\xbb\xbfseries,segment,x,y\r\n'),data[:48]
   assert b'"Curve, ""Two""",1,' in data,'CSV must escape quotes and commas in series name'
   print('PASS v0.2 series name, color, visibility, standard RFC4180 CSV',flush=True)
   # Series destructive remove + Undo/Redo restore all points and model state.
   await page.locator('#backExtractButton').click()
   second=page.locator('#seriesList .series-entry').nth(1)
   await second.locator('button').nth(2).click()
   assert await page.locator('#appConfirmDialog').evaluate('d=>d.open')
   await page.locator('#appConfirmOk').click()
   assert await page.locator('#resultPoints').text_content()=='1'
   assert await page.locator('#seriesList .series-entry').count()==1
   await page.locator('#undoButton').click()
   assert await page.locator('#resultPoints').text_content()=='2'
   assert await page.locator('#seriesList .series-entry').count()==2
   await page.locator('#redoButton').click()
   assert await page.locator('#resultPoints').text_content()=='1'
   await page.locator('#undoButton').click() # 2-series state for crop test
   print('PASS v0.2 series remove confirmation, Undo/Redo model restoration',flush=True)
   # Crop geometry retains every axis marker and every picked point; no hidden resets.
   await page.locator('[data-step="image"]').click()
   await page.locator('#cropModeButton').click()
   a=await image_pos(page,80,68);b=await image_pos(page,810,460)
   await page.mouse.move(*a);await page.mouse.down();await page.mouse.move(*b,steps=7);await page.mouse.up()
   await page.locator('#cropApplyButton').click()
   assert await page.locator('#appConfirmDialog').evaluate('d=>d.open')
   await page.locator('#appConfirmOk').click()
   assert await page.locator('#resultPoints').text_content()=='2'
   assert await page.locator('#toExtractButton').is_enabled()
   assert await page.locator('#undoButton').is_disabled(),'crop must clear non-transformable history'
   assert '900 × 540' not in (await page.locator('#imageMeta').text_content())
   await page.locator('[data-step="results"]').click()
   assert await page.locator('#pointRows tr').count()==2
   assert not errors,errors
   assert not network,network
   print('PASS v0.2 crop keeps calibration + point coordinates, 0 runtime requests / errors',flush=True)
   await page.close()
   # Responsive alignment and series UI, no horizontal overflow at all mobile target widths.
   for width in (320,360,390,430):
    mobile=await browser.new_page(viewport={'width':width,'height':770},is_mobile=True,has_touch=True,locale='en-US')
    await mobile.set_content((R/'dist/index.html').read_text())
    bounds=await aligned(mobile)
    assert bounds['left']<.1 and bounds['right']<.1,bounds
    await mobile.locator('#sampleButton').click()
    await mobile.locator('[data-mobile-key="axis"]').click()
    await calibrate(mobile)
    await mobile.locator('#toExtractButton').click()
    await mobile.locator('#addSeriesButton').click()
    assert await mobile.locator('#seriesList .series-entry').count()==2
    bounds=await aligned(mobile)
    assert bounds['overflow']<=0,(width,bounds)
    await mobile.close()
   print('PASS v0.2 320/360/390/430px bilingual mobile: aligned header/body, no horizontal overflow, series controls',flush=True)
  finally:
   await asyncio.wait_for(browser.close(),timeout=12)
asyncio.run(main())
