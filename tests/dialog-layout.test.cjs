const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { gunzipSync } = require('node:zlib');

const root = path.resolve(__dirname, '..');
let html = fs.readFileSync(process.env.APP_HTML || path.join(root, 'src/index.template.html'), 'utf8');
const payload = html.match(/<script id="self-extract-payload" type="application\/octet-stream">([A-Za-z0-9+/=\r\n]+)<\/script>/);
if (payload) html = gunzipSync(Buffer.from(payload[1], 'base64')).toString('utf8');
const css = html.match(/<style>([\s\S]*?)<\/style>/)?.[1];
assert.ok(css, 'read the real application stylesheet, including inside the release wrapper');
const rules = [...css.replace(/\/\*[\s\S]*?\*\//g, '').matchAll(/([^{}]+)\{([^{}]*)\}/g)]
  .map(([, selectors, body]) => ({ selectors: selectors.trim().split(/,\s*/), body }));
const rule = selector => rules.find(item => item.selectors.includes(selector))?.body || '';
const declaration = (body, name, value) => assert.match(body, new RegExp(`(?:^|;)\\s*${name}\\s*:\\s*${value}\\s*(?:;|$)`));

// These are source/CSS contracts and real-handler tests at a small DOM seam.
// Native layout, wheel/touch scrolling, focus containment, and safe-area rendering
// must still be checked in a browser at 393x252, narrow mobile, and desktop sizes.
test('a native modal locks both scrolling roots without locking the nonmodal point editor', () => {
  for (const selector of ['html:has(dialog:modal)', 'body:has(dialog:modal)']) {
    declaration(rule(selector), 'overflow', 'hidden');
    declaration(rule(selector), 'overscroll-behavior', 'none');
  }
  assert.match(html, /<div\b[^>]*id="touchPrecision"[^>]*role="dialog"[^>]*aria-modal="false"/);
  assert.doesNotMatch(css, /(?:html|body):has\([^)]*(?:touchPrecision|role)/);
});

test('only an open confirmation becomes a viewport-bounded flex column', () => {
  const open = rule('.app-confirm-dialog[open]');
  declaration(open, 'display', 'flex');
  declaration(open, 'flex-direction', 'column');
  assert.match(open, /max-height\s*:\s*min\(760px,\s*calc\(100dvh\s*-\s*28px\s*-\s*env\(safe-area-inset-top\)\s*-\s*env\(safe-area-inset-bottom\)\)\)/);
  assert.doesNotMatch(rule('.app-confirm-dialog'), /display\s*:\s*flex/);
  declaration(rule('dialog'), 'overflow', 'hidden');
});

test('confirmation keeps its header while its message and both actions scroll inside', () => {
  declaration(rule('.app-confirm-header'), 'flex', '0 0 auto');
  const body = rule('.app-confirm-body');
  declaration(body, 'min-height', '0');
  declaration(body, 'flex', '1 1 auto');
  declaration(body, 'overflow', 'auto');
  declaration(body, 'overscroll-behavior', 'contain');
  assert.match(html, /<div class="app-confirm-body">\s*<p[^>]*id="appConfirmMessage"[^>]*><\/p>\s*<div class="app-confirm-actions">\s*<button[^>]*id="appConfirmCancel"[^>]*>[\s\S]*?<\/button>\s*<button[^>]*id="appConfirmOk"[^>]*>[\s\S]*?<\/button>\s*<\/div>\s*<\/div>/);
  assert.ok(rules.some(item => item.selectors.includes('.app-confirm-body') && /padding:\s*12px 18px calc\(env\(safe-area-inset-bottom\) \+ 18px\)/.test(item.body)));
});

test('the existing Help scroll chain and nonmodal precision-panel geometry remain intact', () => {
  declaration(rule('#helpDialog[open]'), 'display', 'flex');
  declaration(rule('#helpDialog[open]'), 'flex-direction', 'column');
  declaration(rule('.dialog-header'), 'flex', '0 0 auto');
  declaration(rule('.dialog-body'), 'min-height', '0');
  declaration(rule('.dialog-body'), 'flex', '1 1 auto');
  declaration(rule('.dialog-body'), 'overflow', 'auto');
  assert.match(rule('.dialog-body'), /padding:\s*20px 20px calc\(28px \+ env\(safe-area-inset-bottom\)\)/);
  const precision = rules.filter(item => item.selectors.includes('.touch-precision')).map(item => item.body).join(';');
  assert.match(precision, /max-height:\s*calc\(100dvh - 110px - env\(safe-area-inset-bottom\)\)/);
  declaration(precision, 'overflow-y', 'auto');
  const badge = html.match(/<div class="local-badge">\s*(<svg[\s\S]*?<\/svg>)/)?.[1];
  assert.ok(badge, 'retain the existing local-processing shield');
  assert.match(badge, /aria-hidden="true"/);
  assert.match(badge, /d="M12 3 5 6v5c0 4\.6 2\.8 8 7 10 4\.2-2 7-5\.4 7-10V6z"/);
  assert.match(badge, /d="m9 12 2 2 4-5"/);
});

test('Help excludes layout audit commentary', () => {
  assert.equal(html.includes('helpDialogScroll'), false);
});

function harness() {
  const nodes = new Map();
  const frames = [];
  const document = { activeElement: null };
  class Element {
    constructor() { this.listeners = new Map(); this.isConnected = true; this.open = false; this.classList = { toggle() {} }; }
    addEventListener(type, callback) { const list = this.listeners.get(type) || []; list.push(callback); this.listeners.set(type, list); }
    emit(type, fields = {}) { const event = { target: this, clientX: 50, clientY: 50, prevented: false, preventDefault() { this.prevented = true; }, ...fields }; for (const callback of this.listeners.get(type) || []) callback(event); return event; }
    showModal() { this.open = true; }
    close() { this.open = false; this.emit('close'); }
    focus(options) { this.focusOptions = options; document.activeElement = this; }
    getBoundingClientRect() { return { left: 10, top: 10, right: 100, bottom: 100 }; }
  }
  const $ = selector => { if (!nodes.has(selector)) nodes.set(selector, new Element()); return nodes.get(selector); };
  const origin = $('#origin'); origin.focus();
  const context = vm.createContext({ $, document, HTMLElement: Element, window: {}, translate: key => key, requestAnimationFrame: callback => frames.push(callback) });
  const confirm = html.slice(html.indexOf('      const AppConfirm = (() => {'), html.indexOf('      const AppToast = (() => {'));
  assert.match(confirm, /window.AppConfirm = AppConfirm/);
  vm.runInContext(confirm, context);
  const start = html.indexOf("      const helpDialog=$('#helpDialog');");
  const end = html.indexOf("      const imageInput=$('#imageInput')", start);
  assert.ok(start >= 0 && end > start);
  vm.runInContext(`let helpRestoreFocus = null; ${html.slice(start, end)}`, context);
  return { $, origin, document, ask: context.window.AppConfirm.ask, flush() { while (frames.length) frames.shift()(); } };
}

for (const action of ['close', 'cancel', 'escape', 'backdrop', 'ok']) {
  test(`confirmation ${action} settles once, restores focus, and can reopen`, async () => {
    const h = harness();
    for (let cycle = 0; cycle < 2; cycle++) {
      let settlements = 0;
      const result = h.ask({ title: 'Reset work?', message: 'Synthetic text', tone: 'danger' }).then(value => { settlements++; return value; });
      h.flush();
      assert.equal(h.$('#appConfirmDialog').open, true);
      assert.equal(h.document.activeElement, h.$('#appConfirmCancel'));
      h.$('#appConfirmDialog').emit('click');
      assert.equal(h.$('#appConfirmDialog').open, true, 'an inside click must not dismiss');
      if (action === 'escape') assert.equal(h.$('#appConfirmDialog').emit('cancel').prevented, true);
      else if (action === 'backdrop') h.$('#appConfirmDialog').emit('click', { clientX: 0, clientY: 0 });
      else h.$({ close: '#appConfirmClose', cancel: '#appConfirmCancel', ok: '#appConfirmOk' }[action]).emit('click');
      assert.equal(await result, action === 'ok');
      h.$('#appConfirmCancel').emit('click');
      assert.equal(settlements, 1);
      assert.equal(h.$('#appConfirmDialog').open, false);
      assert.equal(h.document.activeElement, h.origin);
      assert.equal(h.origin.focusOptions.preventScroll, true);
    }
  });
}

test('Help keeps close, native-close restoration, backdrop dismissal, and reopening', () => {
  const h = harness();
  for (const close of ['button', 'native', 'backdrop']) {
    h.$('#helpButton').emit('click');
    assert.equal(h.$('#helpDialog').open, true);
    h.$('#helpDialog').emit('click');
    assert.equal(h.$('#helpDialog').open, true);
    h.$('#helpDialog').emit('click', { target: h.$('#buildSummary'), clientX: 0, clientY: 0 });
    assert.equal(h.$('#helpDialog').open, true, 'keyboard activation of an inner summary stays inside Help');
    if (close === 'button') h.$('#closeHelpButton').emit('click');
    else if (close === 'native') h.$('#helpDialog').close();
    else h.$('#helpDialog').emit('click', { clientX: 0, clientY: 0 });
    assert.equal(h.$('#helpDialog').open, false);
    assert.equal(h.document.activeElement, h.origin);
  }
});

test('the canonical repository gate runs source and both generated modal contracts', () => {
  const gate = fs.readFileSync(path.join(root, 'scripts/check-repository.ps1'), 'utf8');
  assert.match(gate, /tests[\\/]dialog-layout\.test\.cjs/);
  assert.match(gate, /\$env:APP_HTML\s*=/);
  for (const artifact of ['src/index.template.html', 'dist/index.html', 'dist/index.self-extract.html']) {
    assert.ok(gate.includes(artifact) || gate.includes(artifact.replaceAll('/', '\\')), `gate includes ${artifact}`);
  }
  assert.match(gate, /Modal layout regression tests failed/);
  assert.match(gate, /finally\s*\{[\s\S]*?\$env:APP_HTML\s*=\s*\$previousAppHtml/);
  for (const file of ['build-standalone.yml', 'deploy-pages.yml']) {
    assert.match(fs.readFileSync(path.join(root, '.github/workflows', file), 'utf8'), /\.\/scripts\/check-repository\.ps1/);
  }
});
