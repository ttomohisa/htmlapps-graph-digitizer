"""v0.7.0 regression: linked review/repair, segment repair, CSV target/preview, no-review CTA hiding."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]
TMP=R/'tests/.tmp-v070';TMP.mkdir(exist_ok=True)
async def click_pt(page,px,py):
    c=page.locator('#graphCanvas');await c.scroll_into_view_if_needed();box=await c.bounding_box();assert box
    await page.mouse.click(box['x']+box['width']*px/900,box['y']+box['height']*py/540);await page.wait_for_timeout(30)
async def calibrate(page):
    for p in ((96,420),(770,420),(96,420),(96,85)):await click_pt(page,*p)
async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
    try:
      html=(R/'dist/index.html').read_text()
      maker=await browser.new_page(viewport={'width':1440,'height':1000},locale='ja-JP',accept_downloads=True)
      await maker.set_content(html,wait_until='load');await maker.locator('#sampleButton').click();await calibrate(maker);await maker.locator('#toExtractButton').click()
      await maker.locator('#tracePickColorButton').click();await click_pt(maker,433,298);await maker.locator('#traceAxisRangeButton').click();await maker.locator('#traceRunButton').click();await maker.locator('#traceApplyButton').wait_for(state='visible',timeout=10000);await maker.locator('#traceApplyButton').click()
      base=TMP/'base.graphdigitizer.json'
      async with maker.expect_download() as info: await maker.locator('#projectSaveExtractButton').click()
      await (await info.value).save_as(str(base));doc=json.loads(base.read_text())
      first=doc['series'][0];first['name']='Series, "A"'
      pts=[x for x in doc['points'] if x['seriesId']==first['id']];assert len(pts)>250
      pts[40]['needsReview']=True
      for x in pts[len(pts)//2:]:x['segmentId']=2
      doc['series'].append({'id':'s-2','name':'Manual B','color':'#c05d36','visible':True});doc['seriesSequence']=2
      doc['points'].append({'id':'p-9999','seriesId':'s-2','segmentId':1,'px':500,'py':250,'source':'manual','needsReview':False});doc['idSequence']=9999;doc['activeSeriesId']='s-1';doc['export']['csvTarget']='all';doc['workflowStep']='results'
      fixture=TMP/'review.graphdigitizer.json';fixture.write_text(json.dumps(doc),encoding='utf-8')
      await maker.close()

      page=await browser.new_page(viewport={'width':1366,'height':900},locale='ja-JP',accept_downloads=True)
      errors=[];network=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None)
      await page.set_content(html,wait_until='load');await page.locator('#projectInput').set_input_files(str(fixture));await page.locator('#resultsPage').wait_for(state='visible',timeout=10000)
      assert await page.locator('#resultReview').text_content()=='1';assert int(await page.locator('#resultSegments').text_content())==3
      assert not await page.locator('#reviewNextButton').is_hidden();assert await page.locator('.review-item').count()>=2
      await page.locator('#reviewNextButton').click();assert await page.locator('#pointRows tr[aria-selected="true"]').count()==1;assert await page.locator('#reviewMarkButton').is_enabled()
      await page.locator('#reviewMarkButton').click();assert await page.locator('#resultReview').text_content()=='0';assert await page.locator('#reviewNextButton').is_hidden(), 'zero-review shortcut must disappear'
      # Segment gap remains listed and can be merged with its previous segment.
      gap=page.locator('.review-item').first;await gap.click();assert await page.locator('#segmentMergeButton').is_enabled();before=int(await page.locator('#resultSegments').text_content());await page.locator('#segmentMergeButton').click();after=int(await page.locator('#resultSegments').text_content());assert after==before-1,(before,after)
      await page.locator('#resultUndoButton').click();assert int(await page.locator('#resultSegments').text_content())==before
      # Detailed graph/table are intentionally collapsed in v0.8.2 to keep Results compact.
      await page.locator('#dataReviewDetails').evaluate('e=>e.open=true')
      # Table selection remains on Results and chart keyboard selection links to table.
      rows=page.locator('#pointRows tr');await rows.nth(20).locator('button').click();assert await page.locator('#resultsPage').is_visible();selected_before=await page.locator('#pointRows tr[aria-selected="true"]').get_attribute('data-point-id')
      await page.locator('#resultChart').focus();await page.locator('#resultChart').press('Enter');selected_after=await page.locator('#pointRows tr[aria-selected="true"]').get_attribute('data-point-id');assert selected_after and selected_after!=selected_before
      # Split at a non-first point, then undo.
      await rows.nth(20).locator('button').click();assert await page.locator('#segmentSplitButton').is_enabled();seg_before=int(await page.locator('#resultSegments').text_content());await page.locator('#segmentSplitButton').click();assert int(await page.locator('#resultSegments').text_content())==seg_before+1;await page.locator('#resultUndoButton').click()
      # Series-targeted CSV preview and RFC4180 escaping.
      await page.locator('#csvPreviewDetails').evaluate('e=>e.open=true')
      opts=page.locator('#csvSeriesTarget option');assert await opts.count()==3
      await page.locator('#csvSeriesTarget').select_option('s-1');preview=await page.locator('#csvPreview').input_value();assert '"Series, ""A"""' in preview;assert 'Manual B' not in preview
      # Second series is a single segment, so simple x,y is available.
      await page.locator('#csvSeriesTarget').select_option('s-2');assert not await page.locator('#csvFormat option[value="simple"]').is_disabled();await page.locator('#csvFormat').select_option('simple');preview=await page.locator('#csvPreview').input_value();assert preview.startswith('x,y\n') and 'Manual B' not in preview
      async with page.expect_download() as info:await page.locator('#downloadButton').click()
      out=TMP/'target.csv';await (await info.value).save_as(str(out));text=out.read_text(encoding='utf-8-sig');assert text.startswith('x,y\n') and len(text.strip().splitlines())==2
      await page.locator('#selectCsvButton').click();assert await page.locator('#csvPreview').evaluate('e=>e.selectionStart===0 && e.selectionEnd===e.value.length')
      assert not errors,errors;assert not network,network
      print('PASS v0.7 review: linked selection, zero-review CTA hiding, gap merge/split+Undo, series-target CSV preview/download',flush=True)
      # Mobile Results must fit at 320px.
      mobile=await browser.new_page(viewport={'width':320,'height':760},is_mobile=True,has_touch=True,locale='ja-JP');await mobile.set_content(html,wait_until='load');await mobile.locator('#projectInput').set_input_files(str(fixture));await mobile.locator('[data-mobile-key="results"]').click();assert await mobile.evaluate('document.documentElement.scrollWidth<=innerWidth');assert await mobile.locator('#reviewPanel').is_visible();assert await mobile.locator('#csvPreviewDetails').is_visible();print('PASS v0.7 mobile 320px compact review/export has no horizontal overflow',flush=True);await mobile.close()
    finally:await browser.close()
asyncio.run(main())
