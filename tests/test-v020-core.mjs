import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const html=readFileSync(new URL('../src/index.template.html',import.meta.url),'utf8');
const source=html.match(/^\s*\/\/ GD:MATH:BEGIN[^\n]*\n([\s\S]*?)^\s*\/\/ GD:MATH:END/m)?.[1];
assert.ok(source,'source math boundary');
const core=vm.runInNewContext(`${source};({linearAxis,mapImagePoint,sortedSeriesValues,exportCSV,imageToScreen,screenToImage})`,{Blob,Map});
const near=(a,b,tol=1e-8)=> assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);
const cal={x:{p1:{px:96,py:420,value:0},p2:{px:770,py:420,value:100}},y:{p1:{px:96,py:420,value:0},p2:{px:96,py:85,value:50}}};
const series=[{id:'s-1',name:'First, "Run"',color:'#16624f',visible:false},{id:'s-2',name:'テスト\n第二系列',color:'#7a594d',visible:true}];
const points=[
 {id:'p3',seriesId:'s-2',segmentId:1,px:433,py:252.5},
 {id:'p1',seriesId:'s-1',segmentId:1,px:96,py:420},
 {id:'p2',seriesId:'s-1',segmentId:1,px:433,py:252.5},
 {id:'p4',seriesId:'s-1',segmentId:1,px:433,py:300},
 {id:'p5',seriesId:'s-1',segmentId:2,px:200,py:310},
];
const rows=core.sortedSeriesValues(points,cal,series);
assert.equal(rows.map(p=>p.id).join(','),'p1,p2,p4,p5,p3');
const bytes=new Uint8Array(await core.exportCSV(points,cal,series).arrayBuffer());
assert.deepEqual(Array.from(bytes.subarray(0,3)),[239,187,191]);
const csv=new TextDecoder().decode(bytes);
assert.ok(csv.startsWith('series,segment,x,y\r\n"First, ""Run""",1,0,0\r\n'));
assert.ok(csv.includes('"テスト\n第二系列",1,50,25\r\n'),'escaped multiline name');
assert.throws(()=>core.exportCSV(points,cal,series,'simple'),/Simple format/);
const only=await core.exportCSV(points.filter(p=>p.id==='p2').map(p=>({...p,seriesId:'s-2'})),cal,[series[1]],'simple').text();
assert.equal(only,'x,y\r\n50,25\r\n');
const img={width:900,height:540},size={width:500,height:300};
for(const view of [{zoom:1,panX:0,panY:0},{zoom:2.6,panX:-146,panY:-55},{zoom:9.9,panX:-1200,panY:-1400}]){
 for(const pt of [{px:433,py:252.5},{px:0,py:540},{px:900,py:0}]){
  const screen=core.imageToScreen(pt,size,img,view);
  const back=core.screenToImage(screen,size,img,view);
  near(back.px,pt.px);near(back.py,pt.py);
 }
}
console.log('PASS v0.2 core: multi-series + segments sort, RFC4180 CSV escaping/BOM, simple export restrictions, zoom/pan coordinate round trips');
