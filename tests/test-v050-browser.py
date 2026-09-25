"""v0.5.0 regression: bundled PDF.js, protected/corrupt errors, page crop/apply, mobile precision placement."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]
F=R/'tests/fixtures'

async def canvas_click(page, selector, fx, fy):
    c=page.locator(selector);await c.scroll_into_view_if_needed();box=await c.bounding_box();assert box
    await page.mouse.click(box['x']+box['width']*fx,box['y']+box['height']*fy);await page.wait_for_timeout(40)

async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
    try:
      page=await browser.new_page(viewport={'width':1366,'height':900},locale='ja-JP')
      errors=[];network=[]
      page.on('pageerror',lambda e:errors.append(str(e)))
      page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None)
      await page.set_content((R/'dist/index.html').read_text(),wait_until='load')
      await page.locator('#sampleButton').click();assert 'サンプル' in (await page.locator('#imageMeta').text_content())
      # Corrupt PDF reports a specific PDF error and preserves current work after closing staging.
      await page.locator('#pdfInput').set_input_files(str(F/'corrupt.pdf'))
      for _ in range(30):
        if 'PDFを開けません' in (await page.locator('#pdfStatus').text_content()): break
        await page.wait_for_timeout(100)
      assert 'PDFを開けません' in (await page.locator('#pdfStatus').text_content())
      await page.locator('#pdfCancelButton').click();assert 'サンプル' in (await page.locator('#imageMeta').text_content())
      # Password protected PDF is separated from generic parse errors.
      await page.locator('#pdfInput').set_input_files(str(F/'protected.pdf'))
      for _ in range(30):
        if 'パスワード' in (await page.locator('#pdfStatus').text_content()): break
        await page.wait_for_timeout(100)
      assert 'パスワード' in (await page.locator('#pdfStatus').text_content())
      await page.locator('#pdfCancelButton').click()
      # Multi-page PDF uses local embedded worker/assets; choose page 2 and crop.
      await page.locator('#pdfInput').set_input_files(str(F/'sample-2pages.pdf'))
      await page.locator('#pdfPageSelect').wait_for(state='visible',timeout=12000)
      
      for _ in range(80):
        if await page.locator('#pdfPageSelect option').count()==2: break
        await page.wait_for_timeout(100)
      assert await page.locator('#pdfPageSelect option').count()==2
      assert await page.locator('#pdfStageWrap').is_visible()
      await page.locator('#pdfPageSelect').select_option('2')
      
      for _ in range(80):
        if '×' in (await page.locator('#pdfRenderMeta').text_content()): break
        await page.wait_for_timeout(100)
      assert '×' in (await page.locator('#pdfRenderMeta').text_content())
      await page.locator('#pdfCropButton').click();canvas=page.locator('#pdfCanvas');await canvas.scroll_into_view_if_needed();box=await canvas.bounding_box();assert box
      await page.mouse.move(box['x']+box['width']*.10,box['y']+box['height']*.18);await page.mouse.down();await page.mouse.move(box['x']+box['width']*.92,box['y']+box['height']*.88,steps=8);await page.mouse.up()
      assert '選択範囲' in (await page.locator('#pdfUseButton').text_content())
      # Current sample still exists until final apply; applying asks before replacement.
      await page.locator('#pdfUseButton').click();await page.locator('.app-confirm-dialog[open]').wait_for(timeout=3000)
      await page.locator('#appConfirmOk').click()
      
      for _ in range(50):
        if '-p2' in (await page.locator('#imageMeta').text_content()): break
        await page.wait_for_timeout(100)
      assert '-p2' in (await page.locator('#imageMeta').text_content())
      assert await page.locator('#pdfCard').is_hidden();assert await page.locator('#toAxisButton').is_enabled()
      meta=await page.locator('#imageMeta').text_content();print('PDF applied:',meta,flush=True)
      assert not errors,errors;assert not network,network
      print('PASS v0.5 PDF: corrupt/password separation, 2-page selection, crop/apply, work preservation, 0 network',flush=True)

      # Mobile touch placement opens precision UI instead of immediately committing.
      mobile=await browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='ja-JP')
      merr=[];mnet=[];mobile.on('pageerror',lambda e:merr.append(str(e)));mobile.on('request',lambda r:mnet.append(r.url) if r.url.startswith(('http:','https:')) else None)
      await mobile.set_content((R/'dist/index.html').read_text(),wait_until='load');await mobile.locator('#sampleButton').click();await mobile.locator('[data-mobile-key="axis"]').click()
      c=mobile.locator('#graphCanvas');await c.scroll_into_view_if_needed();box=await c.bounding_box();assert box
      # Touch first known axis marker; precision panel should intercept commit.
      await mobile.touchscreen.tap(box['x']+box['width']*96/900,box['y']+box['height']*420/540);await mobile.wait_for_timeout(120)
      assert await mobile.locator('#touchPrecision').is_visible();before=await mobile.locator('#touchPrecisionCoords').text_content()
      await mobile.locator('[data-nudge="1,0"]').click();after=await mobile.locator('#touchPrecisionCoords').text_content();assert before!=after,(before,after)
      await mobile.locator('#touchPrecisionApply').click();assert await mobile.locator('#touchPrecision').is_hidden();assert '未設定' not in (await mobile.locator('[data-axis-point="x1"]').text_content())
      assert await mobile.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
      assert not merr,merr;assert not mnet,mnet
      print('PASS v0.5 mobile: touch draft, magnifier/nudge/confirm, no horizontal overflow',flush=True)

      # PDF staging controls must remain usable at Browser Kitty target mobile widths.
      for width in (320,360,390,430):
        mp=await browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True,locale='ja-JP')
        perr=[];pnet=[];mp.on('pageerror',lambda e,bag=perr:bag.append(str(e)));mp.on('request',lambda r,bag=pnet:bag.append(r.url) if r.url.startswith(('http:','https:')) else None)
        await mp.set_content((R/'dist/index.html').read_text(),wait_until='load')
        assert await mp.locator('#choosePdfButton').is_visible()
        await mp.locator('#pdfInput').set_input_files(str(F/'sample-2pages.pdf'))
        await mp.locator('#pdfPageSelect').wait_for(state='visible',timeout=12000)
        for _ in range(80):
          if await mp.locator('#pdfPageSelect option').count()==2: break
          await mp.wait_for_timeout(100)
        assert await mp.locator('#pdfPageSelect option').count()==2
        assert await mp.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),width
        for selector in ('#pdfPrevButton','#pdfPageSelect','#pdfNextButton','#pdfCropButton','#pdfUseButton','#pdfCancelButton'):
          rect=await mp.locator(selector).bounding_box();assert rect,(width,selector)
          assert rect['x']>=-1 and rect['x']+rect['width']<=width+1,(width,selector,rect)
        assert not perr,(width,perr);assert not pnet,(width,pnet)
        await mp.close()
      print('PASS v0.5 mobile PDF: 320/360/390/430px staging controls fit with no horizontal overflow',flush=True)
    finally:await browser.close()

asyncio.run(main())
