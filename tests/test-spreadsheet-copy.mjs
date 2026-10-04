import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const html=readFileSync(new URL('../src/index.template.html',import.meta.url),'utf8');
const math=html.match(/^\s*\/\/ GD:MATH:BEGIN[^\n]*\n([\s\S]*?)^\s*\/\/ GD:MATH:END/m)[1];
const core=vm.runInNewContext(`${math};({exportCSVText,exportTSVText:typeof exportTSVText==='function'?exportTSVText:null})`);
assert.equal(typeof core.exportTSVText,'function','spreadsheet TSV export exists');
const calibration={x:{p1:{px:0,py:100,value:0},p2:{px:100,py:100,value:10},scale:'linear'},y:{p1:{px:0,py:100,value:0},p2:{px:0,py:0,value:20},scale:'linear'}};
const series=[{id:'a',name:'=SUM(1,2)\t"A"\r\n日本語',visible:false},{id:'b',name:'B'}];
const point=(id,seriesId,segmentId,px,py)=>({id,seriesId,segmentId,px,py});
const points=[point('1','a',2,80,50),point('2','a',1,20,75),point('3','a',1,20,25),point('4','b',1,-10,50)];
const before=JSON.stringify({points,series,calibration});
const tsv=core.exportTSVText(points,calibration,series);
assert.equal(tsv,'series\tsegment\tx\ty\r\n\'=SUM(1,2) "A"  日本語\t1\t2\t5\r\n\'=SUM(1,2) "A"  日本語\t1\t2\t15\r\n\'=SUM(1,2) "A"  日本語\t2\t8\t10\r\nB\t1\t-1\t10\r\n');
for(const name of ['=1+1','+SUM(A1)','-1+1','@SUM(A1)',' \t=1','"=1"',"'quoted",'a\u0000b\u0085c\u2028d\u2029e']){
 const text=core.exportTSVText([points[1]],calibration,[{id:'a',name}]);
 const rows=text.trimEnd().split('\r\n');assert.equal(rows.length,2);assert.equal(rows[1].split('\t').length,4);assert.ok(!/^[\s]*[=+\-@"]/.test(rows[1]));
 if(/^[\s]*[=+\-@"']/.test(name))assert.ok(rows[1].startsWith("'"),'dangerous text receives apostrophe');
 assert.ok(!/[\u0000-\u001f\u007f-\u009f\u2028\u2029]/.test(rows[1].split('\t')[0]));
}
assert.ok(core.exportTSVText([points[1]],calibration,[{id:'a',name:'Series A \"quoted\"'}]).includes('Series A \"quoted\"\t'));
assert.equal(core.exportTSVText([points[3]],calibration,[series[1]],'simple'),'x\ty\r\n-1\t10\r\n');
assert.throws(()=>core.exportTSVText(points,calibration,series,'simple'),/one series and one segment/);
assert.throws(()=>core.exportTSVText([],calibration,series,'bogus'),/format/);
assert.throws(()=>core.exportTSVText([point('x','missing',1,1,1)],calibration,series),/missing series/);
assert.equal(core.exportTSVText([],calibration,series),'series\tsegment\tx\ty\r\n');
const small=structuredClone(calibration);small.x.p2.value=1e-8;
assert.equal(core.exportTSVText([point('tiny','b',1,-100,50)],small,[series[1]],'simple'),'x\ty\r\n-1e-8\t10\r\n');
assert.equal(JSON.stringify({points,series,calibration}),before,'export does not mutate source');
assert.ok(core.exportCSVText(points,calibration,series).includes('"=SUM(1,2)\t""A""\r\n日本語"'),'CSV escaping stays unchanged');

const ui=html.match(/\/\/ GD:SPREADSHEET:BEGIN\n([\s\S]*?)\/\/ GD:SPREADSHEET:END/)?.[1];assert.ok(ui,'clipboard controller boundary');
function harness(clipboard){
 const elements=Object.fromEntries(['copySpreadsheetButton','spreadsheetFallback','spreadsheetText','csvFormat'].map(id=>['#'+id,{value:id==='csvFormat'?'standard':'',hidden:true,disabled:false,open:false,focus(){this.focused=true;},select(){this.selected=true;}}]));
 let valid=true,selection={points:Array.from({length:350},(_,i)=>point(String(i),'b',1,i,50)),series:[series[1]]};const messages=[];
 const context={...core,$:id=>elements[id],navigator:{clipboard},currentCalibration:()=>({ok:valid,calibration}),csvSelection:()=>selection,showToast:(...args)=>messages.push(args),translate:key=>key};
 const controller=vm.runInNewContext(`${ui};({copySpreadsheet,renderSpreadsheetCopy})`,context);
 return {...controller,elements,messages,setValid:v=>valid=v,setSelection:s=>selection=s};
}
let copied;let h=harness({writeText:async text=>copied=text});h.renderSpreadsheetCopy({ok:true});await h.copySpreadsheet();assert.equal(copied.split('\r\n').length,352);assert.equal(h.messages.at(-1)[0],'spreadsheetCopied');assert.equal(h.elements['#spreadsheetFallback'].hidden,true);
for(const clipboard of [undefined,{writeText:async()=>{throw Error('denied');}}]){
 h=harness(clipboard);await h.copySpreadsheet();const full=h.elements['#spreadsheetText'];assert.equal(full.value.split('\r\n').length,352,'fallback contains every row');assert.ok(full.focused&&full.selected);assert.equal(h.elements['#spreadsheetFallback'].hidden,false);assert.equal(h.elements['#spreadsheetFallback'].open,true);
 h.renderSpreadsheetCopy({ok:false});assert.equal(full.value,'');assert.equal(h.elements['#spreadsheetFallback'].hidden,true);assert.equal(h.elements['#copySpreadsheetButton'].disabled,true);
}
h=harness(undefined);h.setValid(false);await h.copySpreadsheet();assert.equal(h.messages.length,0);
h=harness(undefined);h.setSelection({points:[],series:[series[1]]});h.renderSpreadsheetCopy({ok:true});await h.copySpreadsheet();assert.equal(h.elements['#copySpreadsheetButton'].disabled,true);assert.equal(h.messages.length,0);
let reject;h=harness({writeText:()=>new Promise((_,r)=>reject=r)});const pending=h.copySpreadsheet();h.renderSpreadsheetCopy({ok:false});reject(Error('late'));await pending;assert.equal(h.messages.length,0,'stale clipboard result stays silent');assert.equal(h.elements['#spreadsheetText'].value,'');
let resolve;h=harness({writeText:()=>new Promise(r=>resolve=r)});const oldSuccess=h.copySpreadsheet();h.renderSpreadsheetCopy({ok:true});resolve();await oldSuccess;assert.equal(h.messages.length,0,'stale success stays silent');
let attempts=0;h=harness({writeText:async()=>{if(++attempts===1)throw Error('first denied');}});await h.copySpreadsheet();assert.equal(h.elements['#spreadsheetFallback'].hidden,false);await h.copySpreadsheet();assert.equal(h.elements['#spreadsheetFallback'].hidden,true);assert.equal(h.elements['#spreadsheetText'].value,'');
h=harness(undefined);h.elements['#csvFormat'].value='simple';h.setSelection({points:[points[3]],series:[series[1]]});await h.copySpreadsheet();assert.equal(h.elements['#spreadsheetText'].value,'x\ty\r\n-1\t10\r\n','controller honors selected simple format');
// Parse every executable inline script, not only the extracted test seams.
for(const match of html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)){
 if(match[0].startsWith('<script type="application/json"'))continue;
 new vm.Script(match[1]);
}
console.log('PASS spreadsheet TSV: safe text cells, numeric fidelity, selected format/order, unchanged CSV, full fallback, invalid/empty/stale guards');
