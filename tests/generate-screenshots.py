"""Capture Graph Digitizer v1.0.0 screenshots from the built standalone HTML."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]
TMP=R/'tests/.tmp-screenshots';TMP.mkdir(exist_ok=True)

async def click_pt(page,px,py):
    c=page.locator('#graphCanvas');await c.scroll_into_view_if_needed();box=await c.bounding_box();assert box
    await page.mouse.click(box['x']+box['width']*px/900,box['y']+box['height']*py/540);await page.wait_for_timeout(30)

async def calibrate(page):
    for p in ((96,420),(770,420),(96,420),(96,85)):await click_pt(page,*p)

async def make_review_project(browser,html):
    page=await browser.new_page(viewport={'width':1440,'height':1000},locale='ja-JP',accept_downloads=True)
    await page.set_content(html,wait_until='load');await page.locator('#sampleButton').click();await calibrate(page);await page.locator('#toExtractButton').click()
    await page.locator('#tracePickColorButton').click();await click_pt(page,433,298);await page.locator('#traceAxisRangeButton').click();await page.locator('#traceRunButton').click();await page.locator('#traceApplyButton').wait_for(state='visible',timeout=10000);await page.locator('#traceApplyButton').click()
    base=TMP/'base.graphdigitizer.json'
    async with page.expect_download() as info:await page.locator('#projectSaveExtractButton').click()
    await (await info.value).save_as(str(base));doc=json.loads(base.read_text())
    first=doc['series'][0];first['name']='測定曲線 A';pts=[x for x in doc['points'] if x['seriesId']==first['id']]
    pts[40]['needsReview']=True
    for x in pts[len(pts)//2:]:x['segmentId']=2
    doc['series'].append({'id':'s-2','name':'参考系列 B','color':'#c05d36','visible':True});doc['seriesSequence']=2
    doc['points'].append({'id':'p-9999','seriesId':'s-2','segmentId':1,'px':500,'py':250,'source':'manual','needsReview':False});doc['idSequence']=9999
    doc['activeSeriesId']='s-1';doc['export']['csvTarget']='all';doc['workflowStep']='results'
    fixture=TMP/'review.graphdigitizer.json';fixture.write_text(json.dumps(doc),encoding='utf-8')
    en=json.loads(json.dumps(doc));en['series'][0]['name']='Measurement A';en['series'][1]['name']='Reference B';fixture_en=TMP/'review-en.graphdigitizer.json';fixture_en.write_text(json.dumps(en),encoding='utf-8');await page.close();return fixture,fixture_en

async def load_project(page,html,fixture):
    await page.set_content(html,wait_until='load');await page.locator('#projectInput').set_input_files(str(fixture));await page.locator('#resultsPage').wait_for(state='visible',timeout=10000)
    await page.evaluate("window.AppToast.dismiss();window.scrollTo({top:0,behavior:'instant'})");await page.wait_for_timeout(120)

async def load_sample(page):
    await page.locator('#sampleButton').click()
    mobile_image=page.locator('[data-mobile-key="image"]');desktop_image=page.locator('[data-step="image"]')
    if await mobile_image.count() and await mobile_image.is_visible():await mobile_image.click()
    elif await desktop_image.count() and await desktop_image.is_visible():await desktop_image.click()
    await page.evaluate("window.AppToast.dismiss();window.scrollTo({top:0,behavior:'instant'})");await page.wait_for_timeout(120)

async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
    try:
      html=(R/'dist/index.html').read_text();fixture,fixture_en=await make_review_project(browser,html)
      page=await browser.new_page(viewport={'width':1366,'height':900},device_scale_factor=1,locale='ja-JP')
      await page.set_content(html,wait_until='load');await page.evaluate('window.AppToast.dismiss()');await page.screenshot(path=str(R/'assets/screenshot-empty.png'),full_page=True)
      await page.locator('#projectInput').set_input_files(str(fixture));await page.locator('#resultsPage').wait_for(state='visible',timeout=10000);await page.evaluate('window.AppToast.dismiss()')
      await page.locator('#reviewPanel').scroll_into_view_if_needed();await page.wait_for_timeout(100)
      await page.screenshot(path=str(R/'assets/screenshot.png'),full_page=True)
      print('Screenshot: Japanese desktop compact review / CSV export workflow',flush=True)
      await page.close()
      english=await browser.new_page(viewport={'width':1366,'height':900},device_scale_factor=1,locale='en-US')
      await english.set_content(html,wait_until='load');await english.locator('#projectInput').set_input_files(str(fixture_en));await english.locator('#resultsPage').wait_for(state='visible',timeout=10000);await english.evaluate("window.AppToast.dismiss();window.scrollTo({top:0,behavior:'instant'})");await english.wait_for_timeout(100)
      await english.screenshot(path=str(R/'assets/screenshot-en.png'),full_page=True)
      print('Screenshot: English desktop compact review / CSV export workflow',flush=True);await english.close()

      mobile=await browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True,locale='ja-JP')
      await load_project(mobile,html,fixture);await mobile.locator('[data-mobile-key="results"]').click();await mobile.locator('#reviewPanel').scroll_into_view_if_needed();await mobile.wait_for_timeout(100)
      assert await mobile.evaluate('document.documentElement.scrollWidth <= window.innerWidth');await mobile.screenshot(path=str(R/'assets/screenshot-mobile.png'),full_page=False)
      print('Screenshot: Japanese 390px compact review workflow',flush=True);await mobile.close()

      precision=await browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True,locale='ja-JP')
      await precision.set_content(html,wait_until='load');await load_sample(precision);await precision.locator('[data-mobile-key="axis"]').click();canvas=precision.locator('#graphCanvas');await canvas.scroll_into_view_if_needed();box=await canvas.bounding_box();assert box
      await precision.touchscreen.tap(box['x']+box['width']*96/900,box['y']+box['height']*420/540);await precision.wait_for_timeout(120);assert await precision.locator('#touchPrecision').is_visible();assert await precision.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
      await precision.screenshot(path=str(R/'assets/screenshot-mobile-series.png'),full_page=False);print('Screenshot: Japanese 390px touch precision placement',flush=True);await precision.close()
    finally:await browser.close()
asyncio.run(main())
