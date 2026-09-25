"""v0.8.0 robustness/accessibility regression."""
import asyncio
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]
TMP=R/'tests/.tmp-v080';TMP.mkdir(exist_ok=True)
Image.new('RGB',(3000,3000),'white').save(TMP/'large.png',optimize=True)
Image.new('RGB',(5000,4000),'white').save(TMP/'too-many-pixels.png',optimize=True)
(TMP/'broken.png').write_bytes(b'not a png')
LONG=('very-long-graph-name-'*18)+'figure.png'
async def confirm(page):
    await page.locator('#appConfirmDialog[open]').wait_for(state='visible',timeout=3000)
    await page.locator('#appConfirmOk').click()
async def main():
  async with async_playwright() as p:
    browser=await p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
    try:
      html=(R/'dist/index.html').read_text()
      page=await browser.new_page(viewport={'width':320,'height':568},is_mobile=True,has_touch=True,locale='ja-JP')
      await page.add_init_script("Object.defineProperty(navigator,'deviceMemory',{get:()=>2,configurable:true})")
      errors=[];network=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None)
      await page.set_content(html,wait_until='load')
      await page.evaluate("Object.defineProperty(navigator,'deviceMemory',{get:()=>2,configurable:true})")
      assert await page.locator('#versionBadge').text_content()=='v1.0.0'
      assert await page.evaluate("matchMedia('(prefers-reduced-motion: reduce)') !== null")
      # Help: factual local-processing and unsupported scope; focus returns to opener.
      await page.locator('#helpButton').focus();await page.locator('#helpButton').click();assert await page.locator('#helpDialog').is_visible()
      text=await page.locator('#helpDialog').inner_text();assert '棒グラフ' in text and 'サーバーへアップロードしません' in text
      await page.locator('#closeHelpButton').click();assert await page.evaluate("document.activeElement?.id")=='helpButton'
      # Large image on low-memory device loads but gives actionable warning.
      await page.locator('#imageInput').set_input_files(str(TMP/'large.png')); await page.locator('#imageMeta').wait_for(state='visible'); await page.wait_for_function("document.querySelector('#imageMeta').textContent.includes('3000')")
      assert '大きいため' in (await page.locator('#resourceStatus').text_content())
      assert await page.locator('#toAxisButton').is_enabled()
      # Long names must not create horizontal scroll.
      await page.locator('#imageInput').set_input_files({'name':LONG,'mimeType':'image/png','buffer':(TMP/'large.png').read_bytes()});await confirm(page)
      for _ in range(30):
        if 'very-long' in (await page.locator('#imageMeta').text_content()): break
        await page.wait_for_timeout(100)
      assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth')
      # >16MP rejection preserves current image/work.
      before=await page.locator('#imageMeta').text_content()
      await page.locator('#imageInput').set_input_files(str(TMP/'too-many-pixels.png'));await confirm(page)
      for _ in range(30):
        if '1600' in (await page.locator('#imageStatus').text_content()): break
        await page.wait_for_timeout(100)
      after=await page.locator('#imageMeta').text_content()
      assert before==after and '1600' in (await page.locator('#imageStatus').text_content())
      # Invalid image bytes preserve current work and tell the user what happened.
      await page.locator('#imageInput').set_input_files(str(TMP/'broken.png'));await confirm(page)
      for _ in range(30):
        if '読み込めません' in (await page.locator('#imageStatus').text_content()): break
        await page.wait_for_timeout(100)
      assert await page.locator('#imageMeta').text_content()==after
      assert '読み込めません' in (await page.locator('#imageStatus').text_content())
      # 200% browser zoom equivalent via CSS zoom should not create horizontal overflow at short mobile height.
      await page.evaluate("document.documentElement.style.zoom='2'");await page.wait_for_timeout(100)
      assert await page.evaluate('document.documentElement.scrollWidth<=innerWidth*1.05')
      # English help must expose same scope/privacy facts.
      await page.evaluate("document.documentElement.style.zoom='1'");await page.locator('#languageButton').click();await page.locator('#helpButton').click();en=await page.locator('#helpDialog').inner_text();assert 'Bar charts' in en and 'not uploaded at runtime' in en;await page.locator('#closeHelpButton').click()
      assert not errors,errors;assert not network,network
      print('PASS v0.8 robustness: low-memory large-image advice, invalid/oversize preservation, long names, help scope/privacy, focus restore, 320x568/zoom layout',flush=True)
    finally:await browser.close()
asyncio.run(main())
