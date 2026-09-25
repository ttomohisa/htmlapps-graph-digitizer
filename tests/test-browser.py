"""Local Chromium integration check; run with installed Playwright and Chromium.
Manual Safari/Android/Windows Edge checks remain release prerequisites.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
R=Path(__file__).resolve().parents[1]
# This managed Chromium blocks direct file:// and localhost navigation.
# Use in-memory rendering; keep direct file:// verification a separate Windows/manual gate.

async def point(page, px, py, iw=900, ih=540):
    c=page.locator('#graphCanvas')
    await c.scroll_into_view_if_needed()
    box=await c.bounding_box()
    assert box, 'canvas not visible'
    await page.mouse.click(box['x']+px/iw*box['width'],box['y']+py/ih*box['height'])
    await page.wait_for_timeout(60)
async def calibrate(page):
    await point(page,96,420)
    await point(page,770,420)
    await point(page,96,420)
    await point(page,96,85)
    assert await page.locator('#toExtractButton').is_enabled(), 'linear axis calibration failed'
async def main():
    async with async_playwright() as playwright:
        browser=await playwright.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
        try:
            page=await browser.new_page(viewport={'width':1366,'height':900},accept_downloads=True,device_scale_factor=1,locale='ja-JP')
            page.set_default_timeout(7000)
            print('BOOT',flush=True)
            errors=[];requests=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('request',lambda request:requests.append(request.url) if request.url.startswith(('http:', 'https:')) else None)
            await page.set_content((R/'dist/index.html').read_text(),wait_until='load')
            assert await page.locator('#downloadButton').is_disabled()
            assert await page.locator('#axisPage').is_hidden()
            await page.locator('#sampleButton').click()
            assert '900 × 540' in (await page.locator('#imageMeta').text_content())
            print('SAMPLE imported',flush=True)
            await calibrate(page)
            # A fifth accidental click after finishing calibration must not overwrite Y2.
            previous_y2=await page.locator('[data-axis-point="y2"]').text_content()
            await point(page,132,144)
            assert await page.locator('[data-axis-point="y2"]').text_content()==previous_y2
            print('CALIBRATED; completed axes cannot be overwritten by accidental clicks',flush=True)
            await page.locator('#axisValueX2').fill('0')
            assert await page.locator('#toExtractButton').is_disabled(),'zero range improperly accepted'
            await page.locator('#axisValueX2').fill('100')
            assert await page.locator('#toExtractButton').is_enabled()
            await page.locator('#toExtractButton').click()
            print('EXTRACT enabled',flush=True)
            await point(page,433,252.5)
            assert '1' == (await page.locator('#resultPoints').text_content())
            await page.locator('#toResultButton').click()
            vals=await page.locator('#pointRows tr td').all_text_contents()
            print('Known midpoint UI result:',vals)
            x=float(vals[2]);y=float(vals[3]);assert abs(x-50)<.3 and abs(y-25)<.3,(x,y)
            await page.locator('#csvFormat').select_option('simple')
            await page.locator('#outputFilename').fill('test-known-points.csv')
            async with page.expect_download() as downloaded:
                await page.locator('#downloadButton').click()
            dl=await downloaded.value
            assert dl.suggested_filename=='test-known-points.csv',dl.suggested_filename
            filename=R/'tests/fixtures/browser-output.csv';await dl.save_as(str(filename))
            contents=filename.read_bytes()
            assert contents.startswith(b'\xef\xbb\xbfx,y\r\n')
            row=contents.decode('utf-8-sig').splitlines()[1]
            a,b=[float(v) for v in row.split(',')];assert abs(a-50)<.3 and abs(b-25)<.3
            filename.unlink()
            await page.locator('#languageButton').click()
            assert await page.locator('#heroTitle').text_content()=='Extract numerical data from graph images'
            assert await page.locator('#resultPoints').text_content()=='1','language switch dropped points'
            # Test selected-point deletion + Undo, without changing the graph image.
            await page.locator('#backExtractButton').click()
            await page.locator('#deletePointButton').click()
            assert await page.locator('#toResultButton').is_disabled()
            await page.locator('#appToastAction').click()
            assert await page.locator('#toResultButton').is_enabled()
            assert not errors,errors
            assert not requests,requests
            print('PASS browser: in-memory HTML image, axis calibration, invalid axis, point, CSV download, lang, undo; 0 requests/errors',flush=True)
            await page.close()
            # The unchanged self-extract loader must unpack to the real app when rendered in memory.
            compact=await browser.new_page(viewport={'width':1280,'height':840})
            compactErrors=[];compactRequests=[]
            compact.on('pageerror',lambda e:compactErrors.append(str(e)))
            compact.on('request',lambda req:compactRequests.append(req.url) if req.url.startswith(('http:', 'https:')) and '127.0.0.1' not in req.url else None)
            await compact.set_content((R/'dist/index.self-extract.html').read_text(),wait_until='load')
            await compact.wait_for_selector('#sampleButton',timeout=12000)
            await compact.locator('#sampleButton').click()
            assert '900 × 540' in (await compact.locator('#imageMeta').text_content())
            assert not compactErrors and not compactRequests,(compactErrors,compactRequests)
            print('PASS browser: gzip self-extract in-memory rendering, no runtime requests/errors')
            await compact.close()
            # Native decode behavior including EXIF and WebP
            testimg=await browser.new_page(viewport={'width':1100,'height':800})
            await testimg.set_content((R/'dist/index.html').read_text())
            await testimg.locator('#imageInput').set_input_files(str(R/'tests/fixtures/T08-orientation-6.jpg'))
            await testimg.wait_for_function("document.getElementById('imageMeta').textContent.includes('×')")
            dims=await testimg.locator('#imageMeta').text_content()
            print('EXIF orientation image:',dims)
            assert '120 × 240' in dims,dims
            await testimg.locator('#imageInput').set_input_files(str(R/'tests/fixtures/T08-test.webp'))
            await testimg.wait_for_timeout(100)
            # Existing image should remain before explicit confirmation.
            assert await testimg.locator('#appConfirmDialog').evaluate('(node) => node.open')
            await testimg.locator('#appConfirmCancel').click()
            assert '120 × 240' in (await testimg.locator('#imageMeta').text_content())
            await testimg.close()
            print('PASS browser: JPEG orientation and image-replacement confirmation')
            # Mobile: full workflow at 320/390; all widths tested for sample layout and overflow.
            for width in (320,360,390,430):
                mobile=await browser.new_page(viewport={'width':width,'height':740},is_mobile=True,has_touch=True,locale='ja-JP')
                mobile.set_default_timeout(5000)
                print('MOBILE width',width,flush=True)
                await mobile.set_content((R/'dist/index.html').read_text())
                await mobile.locator('#sampleButton').click()
                print(' mobile sample',flush=True)
                assert await mobile.locator('[data-mobile-key="axis"]').is_enabled()
                assert await mobile.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),f'horizontal overflow at {width}px'
                if width in (320,390):
                    await mobile.locator('[data-mobile-key="axis"]').click()
                    await calibrate(mobile)
                    await mobile.locator('#toExtractButton').click()
                    await point(mobile,433,252.5)
                    await mobile.locator('[data-mobile-key="results"]').click()
                    assert await mobile.locator('#downloadButton').is_enabled()
                    assert await mobile.evaluate('document.documentElement.scrollWidth<=window.innerWidth'),f'horizontal overflow after extraction at {width}px'
                    await mobile.locator('#helpButton').click()
                    helpBody=mobile.locator('#helpDialog .dialog-body')
                    await helpBody.evaluate('el=>{el.scrollTop=el.scrollHeight}')
                    assert await mobile.locator('#helpDialog').evaluate('el=>el.open')
                    await mobile.locator('#closeHelpButton').click()
                    print(' mobile: full workflow and help',flush=True)
                await mobile.close()
            print('PASS browser: 320/360/390/430px no horizontal overflow; full 320/390px extraction, navigation and help scroll',flush=True)
        finally:
            await asyncio.wait_for(browser.close(),timeout=12)
asyncio.run(main())
