// Cross-platform supplement to the UNCHANGED template PowerShell verifier.
// Runs after an official PowerShell build, or against generated preview assets.
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const root=dirname(dirname(fileURLToPath(import.meta.url)));
const read=path=>readFileSync(join(root,path));
const text=path=>read(path).toString('utf8');
const hash=buffer=>createHash('sha256').update(buffer).digest('hex');
const config=JSON.parse(text('app.config.json'));
const source=text('src/index.template.html');
const html=read('dist/index.html');
const page=html.toString('utf8');
const self=read('dist/index.self-extract.html');
const compact=self.toString('ascii');
const selfManifest=JSON.parse(text('dist/self-extract-manifest.json'));
const dependencyManifest=JSON.parse(text('dist/dependency-manifest.json'));
const required=['AGENTS.md','APP_SPEC.md','src/index.template.html','app.config.json','assets/favicon.svg',
  'components/confirm-dialog.html','components/toast.html','components/mobile-bottom-bar.html',
  'scripts/check-repository.ps1','scripts/verify-standalone.ps1','scripts/verify-self-extract.ps1',
  'scripts/build-self-extract.ps1','build-standalone.ps1','build-standalone.bat',
  '.github/workflows/build-standalone.yml','.github/workflows/deploy-pages.yml',
  'dependencies.json','dependencies.lock.json'];
for(const name of required) assert.ok(existsSync(join(root,name)),`missing template path: ${name}`);
const count=(source,needle)=>(source.match(new RegExp(needle.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'g'))||[]).length;
for(const key of ['__APP_CONFIG_JSON__','__BUILD_MANIFEST_JSON__','__EMBEDDED_ASSET_BUNDLE_JSON__']) {
  assert.equal(count(source,key),1,key);
  assert.ok(!page.includes(key),`unresolved generated placeholder ${key}`);
}
assert.equal(count(source,'__APP_ICON_DATA_URI__'),2);
assert.ok(source.includes('id="appBrandIcon"'));
for(const marker of ['bytesAsync','blobUrlAsync','outputFilename','window.AppToast']) assert.ok(source.includes(marker),marker);
assert.match(page,/connect-src\s+'none'/);
assert.doesNotMatch(page,/<script[^>]+src\s*=\s*["']https?:\/\//);
assert.doesNotMatch(page,/<link[^>]+href\s*=\s*["']https?:\/\//);
const favicon=page.match(/<link[^>]+rel="icon"[^>]+href="(data:image\/svg\+xml;base64,[A-Za-z0-9+/=]+)"/);
const brand=page.match(/<img[^>]+id="appBrandIcon"[^>]+src="(data:image\/svg\+xml;base64,[A-Za-z0-9+/=]+)"/);
assert.ok(favicon && brand,'canonical icon embedding');
assert.equal(favicon[1],brand[1],'header and favicon must be identical');
assert.equal(favicon[1],`data:image/svg+xml;base64,${read('assets/favicon.svg').toString('base64')}`);
assert.equal(dependencyManifest.app.version,config.version);
assert.equal(dependencyManifest.dependencies.length,1);
const [pdfjs]=dependencyManifest.dependencies;
assert.equal(pdfjs.id,'pdfjs');
assert.equal(pdfjs.package,'pdfjs-dist');
assert.equal(pdfjs.version,'6.3.289');
assert.equal(pdfjs.license,'Apache-2.0');
assert.equal(pdfjs.locked,true);
const pdfAssets=Object.fromEntries(pdfjs.assets.map(asset=>[asset.key,asset]));
for(const key of ['core','worker','jbig2','openjpeg','qcms']) assert.ok(pdfAssets[key],`missing embedded PDF.js asset: ${key}`);
assert.equal(pdfAssets.core.sha256,'f401927e692efc7735e0cd528c490d0dd31b7f0972c122b7040df805be45cce4');
assert.equal(pdfAssets.worker.sha256,'a33cfe728c584fdba4fcc1fd54bcdc2f9f2f13889ddbb5b2bd1d0f8cbe49b84e');
assert.equal(pdfAssets.jbig2.sha256,'e6bee67724a7b5436fe8162638e3708cfc8d52b6342db69a49715e30ff27cfdc');
assert.equal(pdfAssets.openjpeg.sha256,'004a0e62db930ba9ff2a22212f4554d0bb57a0635a8287caf70f98117cee14ba');
assert.equal(pdfAssets.qcms.sha256,'663d86126d5f5fcb1c61490f94353e2a8375660b8c5498ab3ebab5a34b08800e');
assert.equal(selfManifest.source.sha256,hash(html));
assert.equal(selfManifest.output.sha256,hash(self));
assert.equal(selfManifest.source.bytes,html.byteLength);
assert.ok(self.every(byte=>byte<128),'template self-extract loader must be ASCII');
const payload=compact.match(/<script id="self-extract-payload" type="application\/octet-stream">([A-Za-z0-9+/=]+)<\/script>/);
assert.ok(payload,'missing gzip payload');
const gzip=Buffer.from(payload[1],'base64');
assert.equal(selfManifest.compressedPayload.sha256,hash(gzip));
assert.deepEqual(gunzipSync(gzip),html,'self-extract must embed byte-for-byte readable HTML');
console.log('PASS template: required files, source markers, canonical SVG and no unresolved placeholders');
console.log('PASS standalone: runtime network CSP, no external script/style, pinned embedded PDF.js dependency');
console.log('PASS self-extract: ASCII template loader, manifest SHA-256 and byte-exact gzip payload');
