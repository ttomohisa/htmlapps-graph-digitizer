"""v0.4.0 regression: log10 axes, live recalculation, redrawn chart, rotated affine calibration."""
import asyncio, math
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]

async def image_pos(page,px,py,width=900,height=540):
    c=page.locator('#graphCanvas');await c.scroll_into_view_if_needed();box=await c.bounding_box();assert box
    return box['x']+box['width']*px/width,box['y']+box['height']*py/height
async def click_pt(page,px,py,width=900,height=540):
    x,y=await image_pos(page,px,py,width,height);await page.mouse.click(x,y);await page.wait_for_timeout(25)

async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
    try:
      page=await browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1,locale='ja-JP')
      errors=[];network=[]
      page.on('pageerror',lambda e:errors.append(str(e)))
      page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None)
      await page.set_content((R/'dist/index.html').read_text(),wait_until='load')
      await page.locator('#sampleButton').click()
      await page.locator('#xAxisScale').select_option('log10')
      await page.locator('#axisValueX1').fill('1');await page.locator('#axisValueX2').fill('100')
      for pt in ((96,420),(770,420),(96,420),(96,85)):await click_pt(page,*pt)
      assert await page.locator('#toExtractButton').is_enabled()
      await page.locator('#toExtractButton').click();await click_pt(page,433,252.5)
      cells=await page.locator('#pointRows tr').first.locator('td').all_text_contents()
      assert abs(float(cells[2])-10)<1e-8,cells
      assert abs(float(cells[3])-25)<1e-8,cells
      await page.locator('[data-step="axis"]').click();await page.locator('#axisValueX2').fill('1000')
      await page.locator('[data-step="results"]').click()
      cells=await page.locator('#pointRows tr').first.locator('td').all_text_contents()
      assert abs(float(cells[2])-math.sqrt(1000))<1e-6,cells
      dims=await page.locator('#resultChart').evaluate('(c)=>[c.width,c.height]');assert dims[0]>200 and dims[1]>100,dims
      assert 'log10' in (await page.locator('#resultChartScale').text_content())
      # invalid log values disable downstream actions and explain the reason
      await page.locator('[data-step="axis"]').click();await page.locator('#axisValueX1').fill('0')
      assert not await page.locator('#toExtractButton').is_enabled()
      assert '0より大きい' in (await page.locator('#axisStatus').text_content())
      print('PASS v0.4 T03 browser: log10 calibration, live point recalculation, invalid-log guidance and redrawn chart',flush=True)
      assert not errors,errors;assert not network,network
      await page.close()

      # Real browser interaction on a synthetic 7-degree rotated graph image.
      rot=await browser.new_page(viewport={'width':1366,'height':900},device_scale_factor=1,locale='en-US')
      await rot.set_content((R/'dist/index.html').read_text(),wait_until='load')
      await rot.evaluate('''async()=>{const c=document.createElement('canvas');c.width=800;c.height=500;const x=c.getContext('2d');x.fillStyle='white';x.fillRect(0,0,c.width,c.height);const a=7*Math.PI/180,cs=Math.cos(a),sn=Math.sin(a),O={x:160,y:390},ex={x:520*cs,y:520*sn},ey={x:300*sn,y:-300*cs};const p=(u,v)=>({x:O.x+u*ex.x+v*ey.x,y:O.y+u*ex.y+v*ey.y});x.strokeStyle='#263d35';x.lineWidth=3;x.beginPath();let q=p(0,0);x.moveTo(q.x,q.y);q=p(1,0);x.lineTo(q.x,q.y);x.stroke();x.beginPath();q=p(0,0);x.moveTo(q.x,q.y);q=p(0,1);x.lineTo(q.x,q.y);x.stroke();const blob=await new Promise(r=>c.toBlob(r,'image/png'));const f=new File([blob],'rotated.png',{type:'image/png'});const dt=new DataTransfer();dt.items.add(f);const input=document.querySelector('#imageInput');input.files=dt.files;input.dispatchEvent(new Event('change',{bubbles:true}));}''')
      await rot.locator('#graphCanvas').wait_for(state='visible')
      a=math.radians(7);cs=math.cos(a);sn=math.sin(a);O=(160,390);ex=(520*cs,520*sn);ey=(300*sn,-300*cs)
      pt=lambda u,v:(O[0]+u*ex[0]+v*ey[0],O[1]+u*ex[1]+v*ey[1])
      for q in (pt(.1,0),pt(.9,0),pt(0,.2),pt(0,.8)):await click_pt(rot,*q,width=800,height=500)
      assert await rot.locator('#toExtractButton').is_enabled(),await rot.locator('#axisStatus').text_content()
      await rot.locator('#toExtractButton').click();q=pt(.5,.5);await click_pt(rot,*q,width=800,height=500)
      cells=await rot.locator('#pointRows tr').first.locator('td').all_text_contents()
      assert abs(float(cells[2])-50)<0.15,cells;assert abs(float(cells[3])-25)<0.15,cells
      print('PASS v0.4 T04 browser: 7-degree rotated straight axes calibrate to known XY values',flush=True)
      await rot.close()
    finally:
      await browser.close()
asyncio.run(main())
