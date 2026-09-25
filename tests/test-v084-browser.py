"""v0.8.4 regression: clean input source layout, direct pan/wheel zoom, marker-aware auto trace."""
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]
F=R/'tests'/'fixtures'
MARKER=F/'T09-marker-line.png'

def make_marker_fixture():
    w,h=920,520
    im=Image.new('RGB',(w,h),'white'); d=ImageDraw.Draw(im)
    left,right,top,bottom=120,870,100,455
    for y in range(top,bottom+1,70): d.line((left,y,right,y),fill=(210,214,216),width=2)
    d.line((left,top,left,bottom),fill=(120,126,130),width=2);d.line((left,bottom,right,bottom),fill=(120,126,130),width=2)
    xs=[125,192,260,327,395,463,532,600,668,735,803,868]
    ys=[388,365,299,267,238,134,156,254,171,287,351,398]
    blue=(0,89,152)
    d.line(list(zip(xs,ys)),fill=blue,width=6,joint='curve')
    for x,y in zip(xs,ys): d.rectangle((x-8,y-8,x+8,y+8),fill=blue)
    im.save(MARKER)

async def click_img(page,px,py,width=920,height=520):
    c=page.locator('#graphCanvas');await c.scroll_into_view_if_needed();box=await c.bounding_box();assert box
    await page.mouse.click(box['x']+box['width']*px/width,box['y']+box['height']*py/height);await page.wait_for_timeout(35)

async def main():
  make_marker_fixture()
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
    try:
      page=await browser.new_page(viewport={'width':1400,'height':900},locale='ja-JP')
      errors=[];network=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None)
      await page.set_content((R/'dist/index.html').read_text(),wait_until='load')
      assert await page.locator('#dropChooseButton').count()==0 and await page.locator('#dropPdfButton').count()==0 and await page.locator('#dropProjectButton').count()==0
      assert await page.locator('.input-source-grid .input-source-button').count()==4
      assert await page.locator('#projectCard').is_hidden()
      assert await page.locator('#panButton').count()==0
      await page.locator('#imageInput').set_input_files(str(MARKER));await page.wait_for_timeout(120)
      await page.locator('[data-step="image"]').click();assert await page.locator('#projectCard').is_visible();await page.locator('[data-step="axis"]').click()
      for key,value in {'x1':'1','x2':'12','y1':'0','y2':'250'}.items():
        inp=page.locator(f'[data-axis-input="{key}"]');await inp.fill(value);await inp.dispatch_event('input')
      for pt in ((120,455),(870,455),(120,455),(120,100)):await click_img(page,*pt)
      await page.locator('#toExtractButton').click();await page.locator('#traceMarkerModeButton').click()
      assert await page.locator('#traceStartSetting').is_hidden()
      await page.locator('#tracePickColorButton').click();await click_img(page,125,388)
      await page.locator('#traceAxisRangeButton').click();await page.locator('#traceRunButton').click();await page.wait_for_timeout(600)
      summary=(await page.locator('#traceSummary').text_content()).strip();assert '12' in summary and 'マーカー' in summary,summary
      # wheel zoom works without Ctrl
      c=page.locator('#graphCanvas');box=await c.bounding_box();assert box
      await c.dispatch_event('wheel',{'deltaY':-180,'clientX':box['x']+box['width']/2,'clientY':box['y']+box['height']/2});await page.wait_for_timeout(50)
      assert (await page.locator('#zoomLabel').text_content())!='100%'
      # drag empty space pans while clicks remain available for digitizing
      before=await c.screenshot();await page.mouse.move(box['x']+box['width']*.86,box['y']+box['height']*.2);await page.mouse.down();await page.mouse.move(box['x']+box['width']*.75,box['y']+box['height']*.3,steps=5);await page.mouse.up();await page.wait_for_timeout(40);after=await c.screenshot();assert before!=after
      assert not errors,errors;assert not network,network
      print('PASS v0.8.4 input layout, direct pan/wheel zoom, marker-aware trace (12 markers)',flush=True)
      await page.close()
      mobile=await browser.new_page(viewport={'width':320,'height':568},is_mobile=True,has_touch=True,locale='ja-JP');await mobile.set_content((R/'dist/index.html').read_text(),wait_until='load')
      assert await mobile.locator('.input-source-grid .input-source-button').count()==4
      assert await mobile.evaluate('document.documentElement.scrollWidth<=innerWidth')
      print('PASS v0.8.4 mobile input source grid has no horizontal overflow',flush=True)
      await mobile.close()
    finally:await browser.close()

asyncio.run(main())
