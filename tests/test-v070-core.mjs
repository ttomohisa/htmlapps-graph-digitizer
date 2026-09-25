import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const html=readFileSync(new URL('../src/index.template.html',import.meta.url),'utf8');
const math=html.match(/^\s*\/\/ GD:MATH:BEGIN[^\n]*\n([\s\S]*?)^\s*\/\/ GD:MATH:END/m)?.[1];
assert.ok(math,'math boundary');
const core=vm.runInNewContext(`${math};({exportCSVText})`);
const calibration={
  x:{p1:{px:0,py:100,value:0},p2:{px:100,py:100,value:10},scale:'linear'},
  y:{p1:{px:0,py:100,value:0},p2:{px:0,py:0,value:20},scale:'linear'}
};
const series=[
  {id:'s-1',name:'Series, "A"',color:'#16624f',visible:true},
  {id:'s-2',name:'Line\nB',color:'#c05d36',visible:true}
];
const points=[
  {id:'p-2',seriesId:'s-1',segmentId:1,px:80,py:50},
  {id:'p-1',seriesId:'s-1',segmentId:1,px:20,py:75},
  {id:'p-3',seriesId:'s-1',segmentId:2,px:90,py:25},
  {id:'p-4',seriesId:'s-2',segmentId:1,px:50,py:50}
];
const csv=core.exportCSVText(points,calibration,series,'standard');
assert.ok(csv.startsWith('series,segment,x,y\r\n'));
assert.ok(csv.includes('"Series, ""A""",1,2,5'));
assert.ok(csv.includes('"Line\nB",1,5,10'));
assert.ok(csv.indexOf(',1,2,5')<csv.indexOf(',1,8,10'),'series/segment rows are X-sorted');
assert.throws(()=>core.exportCSVText(points.filter(p=>p.seriesId==='s-1'),calibration,[series[0]],'simple'),/one series and one segment/);
const simple=core.exportCSVText([points[1],points[0]],calibration,[series[0]],'simple');
assert.equal(simple,'x,y\r\n2,5\r\n8,10\r\n');

const projectSource=html.match(/^\s*\/\/ GD:PROJECT:BEGIN[^\n]*\n([\s\S]*?)^\s*\/\/ GD:PROJECT:END/m)?.[1];
assert.ok(projectSource,'project boundary');
const projectCore=vm.runInNewContext(`${projectSource};({validateProjectDocument})`);
const project={
 format:'browser-kitty.graph-digitizer',formatVersion:1,appVersion:'0.7.0',savedAt:'2026-09-24T00:00:00Z',
 workingImage:{name:'figure',mime:'image/png',width:100,height:100,data:'data:image/png;base64,AA=='},
 calibration:{x:{p1:{px:0,py:100},p2:{px:100,py:100}},y:{p1:{px:0,py:100},p2:{px:0,py:0}}},
 values:{x1:'0',x2:'10',y1:'0',y2:'20'},scales:{x:'linear',y:'linear'},
 series,activeSeriesId:'s-1',seriesSequence:2,
 points:[{id:'p-1',seriesId:'s-1',segmentId:1,px:20,py:75,source:'manual',needsReview:false}],idSequence:1,
 trace:{color:{r:22,g:98,b:79},colorPicked:false,range:null,start:null,tolerance:40,maxJump:12,step:2,maxGap:3},
 export:{csvBase:'graph-data',csvFormat:'standard',csvTarget:'s-2'},workflowStep:'results'
};
assert.equal(projectCore.validateProjectDocument(project).ok,true);
const legacy=structuredClone(project);delete legacy.export.csvTarget;assert.equal(projectCore.validateProjectDocument(legacy).ok,true,'v1 project without optional csvTarget remains valid');
const bad=structuredClone(project);bad.export.csvTarget='missing';assert.equal(projectCore.validateProjectDocument(bad).ok,false);
console.log('PASS v0.7 core: RFC4180 CSV escaping/order, segment-aware simple format, optional series target validation');
