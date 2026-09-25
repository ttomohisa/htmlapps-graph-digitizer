"""v0.6.0 regression: portable project save/restore, dirty protection, corrupt/future rejection, PDF-origin resume."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]
F=R/'tests/fixtures'
TMP=R/'tests/.tmp-v060'
TMP.mkdir(exist_ok=True)

async def canvas_click(page, fx, fy):
    c=page.locator('#graphCanvas');await c.scroll_into_view_if_needed();box=await c.bounding_box();assert box
    await page.mouse.click(box['x']+box['width']*fx,box['y']+box['height']*fy);await page.wait_for_timeout(50)

async def calibrate_log_sample(page):
    for sel,val in [('#axisValueX1','1'),('#axisValueX2','100'),('#axisValueY1','1'),('#axisValueY2','1000')]:
        await page.locator(sel).fill(val);await page.locator(sel).press('Tab')
    await page.locator('#xAxisScale').select_option('log10');await page.locator('#yAxisScale').select_option('log10')
    for fx,fy in [(96/900,420/540),(770/900,420/540),(96/900,420/540),(96/900,85/540)]:await canvas_click(page,fx,fy)
    assert '校正が完了' in (await page.locator('#axisStatus').text_content())

async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
    try:
      html=(R/'dist/index.html').read_text()
      page=await browser.new_page(viewport={'width':1366,'height':900},locale='ja-JP',accept_downloads=True)
      errors=[];network=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None)
      await page.set_content(html,wait_until='load')
      assert await page.locator('#projectOpenButton').is_visible()
      await page.locator('#sampleButton').click();await calibrate_log_sample(page);await page.locator('#toExtractButton').click()

      # Auto trace series 1 from the Browser Kitty green sample curve.
      await page.locator('#tracePickColorButton').click();await canvas_click(page,433/900,298/540)
      await page.locator('#traceAxisRangeButton').click();await page.locator('#traceRunButton').click()
      for _ in range(120):
        if not await page.locator('#traceApplyButton').is_hidden():break
        await page.wait_for_timeout(50)
      assert not await page.locator('#traceApplyButton').is_hidden()
      await page.locator('#traceApplyButton').click()
      auto_count=int((await page.locator('#resultPoints').text_content()) or '0');assert auto_count>100,auto_count

      # Add a second series with a manual point; keep auto and manual source types in one project.
      await page.locator('#addSeriesButton').click();await page.locator('#manualCoordinatesDetails').evaluate('e=>e.open=true');await page.locator('#manualPx').fill('500');await page.locator('#manualPy').fill('250');await page.locator('#manualAddButton').click()
      assert await page.locator('.series-entry').count()==2
      assert '未保存' in (await page.locator('#workStatus').text_content())

      project_path=TMP/'complex.graphdigitizer.json'
      async with page.expect_download() as info:await page.locator('#projectSaveExtractButton').click()
      download=await info.value;await download.save_as(str(project_path))
      project=json.loads(project_path.read_text())
      assert project['format']=='browser-kitty.graph-digitizer' and project['formatVersion']==1
      assert project['scales']=={'x':'log10','y':'log10'} and len(project['series'])==2
      assert any(pt['source']=='auto' for pt in project['points']) and any(pt['source']=='manual' for pt in project['points'])
      assert project['workingImage']['data'].startswith('data:image/png;base64,')
      assert 'pdf' not in project or not project.get('pdf')
      assert 'http://' not in project_path.read_text() and 'https://' not in project_path.read_text()
      assert '保存済み' in (await page.locator('#projectStatus').text_content())
      print(f'project saved: {len(project["points"])} points, {project_path.stat().st_size} bytes',flush=True)

      # Restore in a clean page with no original image/PDF.
      restored=await browser.new_page(viewport={'width':1366,'height':900},locale='ja-JP')
      rerrors=[];rnet=[];restored.on('pageerror',lambda e:rerrors.append(str(e)));restored.on('request',lambda r:rnet.append(r.url) if r.url.startswith(('http:','https:')) else None)
      await restored.set_content(html,wait_until='load');await restored.locator('#projectInput').set_input_files(str(project_path))
      for _ in range(80):
        if '保存済み' in (await restored.locator('#projectStatus').text_content()):break
        await restored.wait_for_timeout(50)
      assert '保存済み' in (await restored.locator('#projectStatus').text_content())
      assert await restored.locator('#xAxisScale').input_value()=='log10' and await restored.locator('#yAxisScale').input_value()=='log10'
      assert await restored.locator('.series-entry').count()==2
      assert int((await restored.locator('#resultPoints').text_content()) or '0')==len(project['points'])
      assert await restored.locator('#outputFilename').input_value()==project['export']['csvBase']
      assert not rerrors,rerrors;assert not rnet,rnet

      # Dirty state follows history: edit -> dirty, Undo to saved snapshot -> clean, Redo -> dirty.
      await restored.locator('[data-step="extract"]').click();saved_count=int((await restored.locator('#resultPoints').text_content()) or '0')
      await restored.locator('#manualCoordinatesDetails').evaluate('e=>e.open=true');await restored.locator('#manualPx').fill('360');await restored.locator('#manualPy').fill('255');await restored.locator('#manualAddButton').click()
      assert '未保存' in (await restored.locator('#workStatus').text_content())
      await restored.locator('#undoButton').click();assert int((await restored.locator('#resultPoints').text_content()) or '0')==saved_count;assert '保存済み' in (await restored.locator('#projectStatus').text_content())
      await restored.locator('#redoButton').click();assert int((await restored.locator('#resultPoints').text_content()) or '0')==saved_count+1;assert '未保存' in (await restored.locator('#workStatus').text_content())
      await restored.locator('#undoButton').click();assert '保存済み' in (await restored.locator('#projectStatus').text_content())

      # Dirty work must trigger confirmation; cancel leaves work untouched.
      await restored.locator('[data-step="extract"]').click();before=int((await restored.locator('#resultPoints').text_content()) or '0')
      await restored.locator('#manualCoordinatesDetails').evaluate('e=>e.open=true');await restored.locator('#manualPx').fill('350');await restored.locator('#manualPy').fill('260');await restored.locator('#manualAddButton').click();assert '未保存' in (await restored.locator('#workStatus').text_content())
      await restored.locator('#projectInput').set_input_files(str(project_path));await restored.locator('.app-confirm-dialog[open]').wait_for(timeout=3000);await restored.locator('#appConfirmCancel').click()
      assert int((await restored.locator('#resultPoints').text_content()) or '0')==before+1

      # Malformed and future-version projects never replace current work.
      corrupt=TMP/'corrupt.graphdigitizer.json';corrupt.write_text('{not json',encoding='utf-8')
      await restored.locator('#projectInput').set_input_files(str(corrupt));await restored.wait_for_timeout(120)
      assert '読み込めません' in (await restored.locator('#appToastMessage').text_content())
      assert int((await restored.locator('#resultPoints').text_content()) or '0')==before+1
      future=TMP/'future.graphdigitizer.json';future_doc=json.loads(project_path.read_text());future_doc['formatVersion']=2;future.write_text(json.dumps(future_doc),encoding='utf-8')
      await restored.locator('#projectInput').set_input_files(str(future));await restored.wait_for_timeout(120)
      assert '新しい形式' in (await restored.locator('#appToastMessage').text_content())
      assert int((await restored.locator('#resultPoints').text_content()) or '0')==before+1
      print('PASS v0.6 project: log/log, multi-series, auto+manual, clean restore, dirty cancel, corrupt/future rejection',flush=True)

      # PDF-origin project must resume without the original PDF: apply page 2, save working image, restore elsewhere.
      pdfpage=await browser.new_page(viewport={'width':1366,'height':900},locale='ja-JP',accept_downloads=True)
      perrors=[];pnet=[];pdfpage.on('pageerror',lambda e:perrors.append(str(e)));pdfpage.on('request',lambda r:pnet.append(r.url) if r.url.startswith(('http:','https:')) else None)
      await pdfpage.set_content(html,wait_until='load');await pdfpage.locator('#pdfInput').set_input_files(str(F/'sample-2pages.pdf'));await pdfpage.locator('#pdfPageSelect').wait_for(state='visible',timeout=12000)
      for _ in range(80):
        if await pdfpage.locator('#pdfPageSelect option').count()==2:break
        await pdfpage.wait_for_timeout(100)
      await pdfpage.locator('#pdfPageSelect').select_option('2')
      for _ in range(80):
        if '×' in (await pdfpage.locator('#pdfRenderMeta').text_content()):break
        await pdfpage.wait_for_timeout(100)
      await pdfpage.locator('#pdfUseButton').click()
      for _ in range(50):
        if '-p2' in (await pdfpage.locator('#imageMeta').text_content()):break
        await pdfpage.wait_for_timeout(100)
      assert '-p2' in (await pdfpage.locator('#imageMeta').text_content())
      await pdfpage.locator('[data-step="image"]').click()
      pdf_project=TMP/'pdf-origin.graphdigitizer.json'
      async with pdfpage.expect_download() as info:await pdfpage.locator('#projectSaveButton').click()
      await (await info.value).save_as(str(pdf_project));doc=json.loads(pdf_project.read_text())
      assert doc['workingImage']['name'].endswith('-p2') and 'data:image/png;base64,' in doc['workingImage']['data']
      assert 'sample-2pages.pdf' not in pdf_project.read_text(), 'original PDF filename/bytes should not be retained beyond working-image name semantics'
      for width in (320,360,390,430):
        resume=await browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True,locale='ja-JP')
        merrors=[];mnet=[];resume.on('pageerror',lambda e,bag=merrors:bag.append(str(e)));resume.on('request',lambda r,bag=mnet:bag.append(r.url) if r.url.startswith(('http:','https:')) else None)
        await resume.set_content(html,wait_until='load');await resume.locator('#projectInput').set_input_files(str(pdf_project))
        for _ in range(80):
          if '-p2' in (await resume.locator('#imageMeta').text_content()):break
          await resume.wait_for_timeout(50)
        assert '-p2' in (await resume.locator('#imageMeta').text_content()) and await resume.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),width
        for selector in ('#projectSaveButton','#projectOpenButton'):
          rect=await resume.locator(selector).bounding_box();assert rect,(width,selector)
          assert rect['x']>=-1 and rect['x']+rect['width']<=width+1,(width,selector,rect)
        assert not merrors,(width,merrors);assert not mnet,(width,mnet)
        await resume.close()
      assert not perrors,perrors;assert not pnet,pnet
      print('PASS v0.6 PDF-origin project: selected working image resumes without original PDF, project controls fit 320/360/390/430px',flush=True)

      assert not errors,errors;assert not network,network
    finally:await browser.close()

asyncio.run(main())
